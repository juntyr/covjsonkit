import xarray as xr

from .decoder import Decoder


class Frame(Decoder):
    def __init__(self, covjson):
        super().__init__(covjson)
        self.domains = self.get_domains()
        self.ranges = self.get_ranges()

    def get_domains(self):
        domains = []
        for coverage in self.coverage.coverages:
            domains.append(coverage["domain"])
        return domains

    def get_ranges(self):
        ranges = []
        for coverage in self.coverage.coverages:
            ranges.append(coverage["ranges"])
        return ranges

    def get_values(self):
        values = {}
        for parameter in self.parameters:
            values[parameter] = []
            for range in self.ranges:
                values[parameter].append(range[parameter]["values"])
        return values

    def get_coordinates(self):
        return self.domains[0]["axes"]

    def to_geopandas(self):
        pass

    def to_xarray(self):
        # dims = ["number", "steps", "points"]
        dims = ["datetimes", "points"]
        dataarraydict = {}

        # Get coordinates
        x = []
        y = []
        z = []
        datetimes = []
        for coord in self.get_coordinates()["composite"]["values"]:
            x.append(float(coord[0]))
            y.append(float(coord[1]))
            z.append(float(coord[2]))

        values = {}
        for parameter in self.parameters:
            values[parameter] = []

        for coverage in self.coverages:
            datetimes.append(coverage["domain"]["axes"]["t"]["values"][0])
            for parameter in self.parameters:
                values[parameter].append(coverage["ranges"][parameter]["values"])

        new_values = {}
        for parameter in self.parameters:
            new_values[parameter] = []
            for i, dt in enumerate(datetimes):
                new_values[parameter].append(values[parameter][i])

        for parameter in self.parameters:
            dataarray = xr.DataArray(new_values[parameter], dims=dims)
            dataarray.attrs["type"] = self.get_parameter_metadata(parameter)["type"]
            dataarray.attrs["units"] = self.get_parameter_metadata(parameter)["unit"][
                "symbol"
            ]
            dataarray.attrs["long_name"] = self.get_parameter_metadata(parameter)[
                "observedProperty"
            ]["id"]
            dataarraydict[dataarray.attrs["long_name"]] = dataarray

        ds = xr.Dataset(
            dataarraydict,
            coords=dict(
                datetimes=(["datetimes"], datetimes),
                points=(["points"], list(range(0, len(x)))),
                x=(["points"], x),
                y=(["points"], y),
                z=(["points"], z),
            ),
        )
        for mars_metadata in self.mars_metadata[0]:
            ds.attrs[mars_metadata] = self.mars_metadata[0][mars_metadata]

        # Add date attribute
        ds.attrs["date"] = self.get_coordinates()["t"]["values"][0]

        return ds
