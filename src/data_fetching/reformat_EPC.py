import json
import glob
import os
import re

search_pattern = os.path.join("./", f"formated_*_n_old.json")
files = glob.glob(search_pattern)

                
lettres = "abcdefghijklmnopqrstuvwxyz"

for file_path in files:
    data = json.load(open(file_path,"r"))
    
    # if "_old.json" in file_path:
    #     continue
    # json.dump(data,open(file_path.replace(".json","_n_old.json"),"w"),indent=4)
    # continue
    print(file_path)

    for article in data:
        id = article["id"]
        contents = article["content"]
        
        new_contents = []
        # prev_number = None
        # prev_lettre = None
        # sub_letter = None
        current_pre = None
        for c in contents:
            # a_id = None
            # match = re.match(r"\((\d+)\)|(\d+)\.|\((\d)\.", c)
            # nombre = None
            # if match:
            #     nombre = match.group(1) if match.group(1) is not None else match.group(2)
                
            #     nombre = nombre if nombre is not None else match.group(3)
                
            #     if match.group(3) is not None:
            #         c = f"({c[len(match.group(0)):].strip()}"
            #     else:
            #         c = c[len(match.group(0)):].strip()
            #     prev_number = nombre
            #     prev_lettre = None
            #     sub_letter = None

            # match = re.match(r"\(([a-z]+)\)", c)
            # lettre = None
            # if match:
            #     # Extraire le nombre
            #     lettre = match.group(1)

            #     if prev_lettre is not None:
            #         i_l = lettres.find(lettre)
            #         i_pl = lettres.find(prev_lettre)
            #         if i_l-1 == i_pl :
            #             prev_lettre = lettre
            #             sub_letter = None
            #         else:
            #             sub_letter = lettre
            #     else:
            #         prev_lettre = lettre
            #     # Supprimer le nombre et les parenthèses de la chaîne
            #     c = c[len(match.group(0)):].strip()

            # if a_id is None and prev_number is not None and lettre is None:
            #     a_id = f"{id}_{prev_number}"
            # if a_id is None and prev_number is not None and lettre is not None and sub_letter is None:
            #     a_id = f"{id}_{prev_number}_{prev_lettre}"
            # if a_id is None and prev_number is not None and lettre is not None and sub_letter is not None:
            #     a_id = f"{id}_{prev_number}_{prev_lettre}_{sub_letter}"
            
            
            # if lettre is None and nombre is None and prev_number is not None:
            #     a_id = f"{id}_{prev_number}_inter"
            # elif lettre is None and nombre is None:
            #     a_id = f"{id}_pre"
            
            # new_contents.append({"id":f"{a_id}","text":c})
            

            if c["id"].endswith("_pre"):
                if current_pre is None:
                    current_pre = c
                else:
                    current_pre["text"] = " ".join([current_pre["text"],c["text"]])
            else:
                new_contents.append(c)
            # new_contents.append(c)
        if current_pre is not None:
            new_contents.insert(0,current_pre)
        
        article["content"] = new_contents

    json.dump(data,open(file_path.replace("_n_old.json",".json"),"w"),indent= 4)
    
    # print(fil)