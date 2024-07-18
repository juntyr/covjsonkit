import json

import pandas as pd
from covjson_pydantic.coverage import Coverage

from .encoder import Encoder


class Shapefile(Encoder):
    def __init__(self, type, domaintype):
        super().__init__(type, domaintype)
        self.covjson["domainType"] = "MultiPoint"
        self.covjson['coverages'] = []

    def add_coverage(self, mars_metadata, coords, values):
        new_coverage = {}
        new_coverage["mars:metadata"] = {}
        new_coverage["type"] = "Coverage"
        new_coverage["domain"] = {}
        new_coverage["ranges"] = {}
        self.add_mars_metadata(new_coverage, mars_metadata)
        self.add_domain(new_coverage, coords)
        self.add_range(new_coverage, values)
        self.covjson['coverages'].append(new_coverage)
        #cov = Coverage.model_validate_json(json.dumps(new_coverage))
        #self.pydantic_coverage.coverages.append(cov)

    def add_domain(self, coverage, coords):
        coverage["domain"]["type"] = "Domain"
        coverage["domain"]["axes"] = {}
        coverage["domain"]["axes"]["t"] = {}
        coverage["domain"]["axes"]["t"]["values"] = coords["t"]
        coverage["domain"]["axes"]["composite"] = {}
        coverage["domain"]["axes"]["composite"]["dataType"] = "tuple"
        coverage["domain"]["axes"]["composite"]["coordinates"] = self.covjson['referencing'][0]['coordinates'] #self.pydantic_coverage.referencing[0].coordinates
        coverage["domain"]["axes"]["composite"]["values"] = coords["composite"]

    def add_range(self, coverage, values):
        for parameter in values.keys():
            param = self.convert_param_id_to_param(parameter)
            coverage["ranges"][param] = {}
            coverage["ranges"][param]["type"] = "NdArray"
            coverage["ranges"][param]["dataType"] = "float"
            coverage["ranges"][param]["shape"] = [len(values[parameter])]
            coverage["ranges"][param]["axisNames"] = [str(param)]
            coverage["ranges"][param]["values"] = values[parameter]  # [values[parameter]]

    def add_mars_metadata(self, coverage, metadata):
        coverage["mars:metadata"] = metadata

    def from_xarray(self, dataset):
        range_dicts = {}

        for data_var in dataset.data_vars:
            self.add_parameter(data_var)
            range_dicts[data_var] = dataset[data_var].values.tolist()

        self.add_reference(
            {
                "coordinates": ["x", "y", "z"],
                "system": {
                    "type": "GeographicCRS",
                    "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
                },
            }
        )

        mars_metadata = {}

        for metadata in dataset.attrs:
            mars_metadata[metadata] = dataset.attrs[metadata]

        coords = {}
        coords["composite"] = []
        coords["t"] = dataset.attrs["date"]

        xy = zip(dataset.x.values, dataset.y.values)
        for x, y in xy:
            coords["composite"].append([x, y])

        self.add_coverage(mars_metadata, coords, range_dicts)
        return self.covjson

    def from_polytope(self, result): 
   
        coords  = {}
        mars_metadata = {}
        range_dict = {}
        dates = []
        lat = 0
        param = 0
        number = 0
        levels = [0]
        step = 0
        self.coord_length = 0

        self.func(result, lat, coords, mars_metadata, param, range_dict, number, step, dates, levels)


        self.add_reference(
            {
                "coordinates": ["x", "y", "z"],
                "system": {
                    "type": "GeographicCRS",
                    "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
                },
            }
        )
        
        for date in range_dict.keys():
            for param in range_dict[date].keys():
                self.coord_length = len(range_dict[date][param])
                self.add_parameter(param)
            break

        for date in range_dict.keys():
            self.add_coverage(mars_metadata, coords[date], range_dict[date])

        #self.add_coverage(mars_metadata, coords, range_dict)
        #return self.covjson
        #with open('data.json', 'w') as f:
        #    json.dump(self.covjson, f)
        return self.covjson


    def func(self, tree, lat, coords, mars_metadata, param, range_dict, number, step, dates, levels):
        if len(tree.children) != 0:
        # recurse while we are not a leaf
            for c in tree.children:
                if c.axis.name != "latitude" and c.axis.name != "longitude" and c.axis.name != "param" and c.axis.name != "date" and c.axis.name != "levelist":
                    mars_metadata[c.axis.name] = c.values[0]
                if c.axis.name == "latitude":
                    lat = c.values[0]
                if c.axis.name == "param":
                    param = c.values
                    for date in dates:
                        for para in param:
                            range_dict[str(date)][para] = []
                if c.axis.name == "date":
                    dates = c.values
                    for date in dates:
                        coords[str(date)] = {}
                        coords[str(date)]['composite'] = []
                        coords[str(date)]['t'] = [str(date) + "Z"]
                    for date in c.values:
                        range_dict[str(date)] = {}
                if c.axis.name == "number":
                    number = c.values
                    for num in number:
                        range_dict[num] = {}
                if c.axis.name == "step":
                    step = c.values
                    for num in number:
                        for para in param:
                            for s in step:
                                range_dict[num][para][s] = []
                if c.axis.name == "levelist":
                    levels = c.values
                    coord_length = len(c.values)

                self.func(c, lat, coords, mars_metadata, param, range_dict, number, step, dates, levels)
        else:
            #vals = len(tree.values)
            tree.values = [float(val) for val in tree.values]
            tree.result = [float(val) for val in tree.result]
            #num_intervals = int(len(tree.result)/len(number))
            #para_intervals = int(num_intervals/len(param))
            len_paras = len(param)
            lev_lens = len(levels)

            for date in dates:
                for level in levels:
                    for val in tree.values:
                        coords[str(date)]['composite'].append([lat, val, level])

            for j, date in enumerate(dates):
                for k, lev in enumerate(levels):
                    for i, para in enumerate(param):
                        range_dict[str(date)][para].append(tree.result[i + (j*(lev_lens*len_paras))+ (k*len_paras)])

