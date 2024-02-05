from pathlib import Path

import scrapy
import logging
import json

class IfcInheritanceSpider(scrapy.Spider):
    # Spider name
    name = "ifc_inheritance_spider"
    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    # Data structure of inheritance tree.
    class_dict = {}
    
    def start_requests(self):
        urls = [
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/annex/annex-c.htm"
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_inheritance_tree)
    
    def parse_inheritance_tree(self, response):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Parse inheritance tree.")
        
        parent_node = {
                "ClassName": "Root",
                "Parent": "",
                "Children": [],
                "Layer": -1
            }
        self.class_dict["ROOT"] = parent_node
        type_name_list = response.xpath("//html/body/table/tr/td[1]/text()").getall()
        for type_name in type_name_list:
            # Replace '&nbsp;' to ' '.
            type_name = type_name.replace('\xa0', ' ')
            layer = type_name.count(' ')
            curr_node = {
                "ClassName": type_name.strip(),
                "Parent": "",
                "Children": [],
                "Layer": layer
            }
            
            # Find the parent node of the current node.
            while parent_node["Layer"] >= curr_node["Layer"]:
                parent_node = self.class_dict[parent_node["Parent"]]
            curr_node["Parent"] = parent_node["ClassName"].upper()
            parent_node["Children"].append(curr_node["ClassName"].upper())
            parent_node = curr_node
            
            # Cache in dict.
            self.class_dict[curr_node["ClassName"].upper()] = curr_node
            
        # Persistence.
        with open("ifc_inheritance.json", "w") as jsonFile:
            json.dump(self.class_dict, jsonFile)