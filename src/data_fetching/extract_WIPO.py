import fitz  # PyMuPDF
import json
import re

lettres = "abcdefghijklmnopqrstuvwxyz"

def extract_articles_from_pdf(pdf_path, start_page, end_page):
    """Extrait le texte d'un fichier PDF entre les pages start_page et end_page (inclus)."""
    doc = fitz.open(pdf_path)
    text = []

    articles = []
    chapter = None
    content = []
    id = None
    title = None
    prev_letter = None
    digit = None
    for page_num in range(start_page - 1, end_page):
        # print(doc[page_num].get_text("blocks"))
        c_page= [
            e[4] for e in doc[page_num].get_text("blocks")
        ]
        for ic,para in enumerate(c_page[2:]):
            if "Editor’s Note" in para:
                continue
            
            if para.upper() == para:
                tmp = para.replace("\n","").strip()
                if tmp != "":
                    chapter = tmp
                continue
            
            match = re.match(r"Article (\d+)",para)
            if match:
                if id is not None:
                    articles.append({"id":id,"title":title,"chapter":chapter,"content":content})
                content = []
                prev_letter = None
                digit = None
                id = f"WIPO_A{match.group(1)}"
                title = para.replace("\n","").strip()
                
                continue
            
            # if id != "WIPO_A2":
            #     continue   
            # print(para)
            
            matches = re.findall(r"\n\((\d+)\)\(([a-z]+)\)|\n\((\d+)\)|\n\(([a-z]+)\)",para,re.MULTILINE)
            
            if len(matches) == 0 and len(content) > 0:
                content[-1]["text"] += " " + para
                continue
            elif len(matches) == 0 and len(content) < 1: 
                id_c = f"{id}_pre"
                content.append({"id":id_c,"text":para.replace("\n"," ").strip()})
                
            prev_m = None
            recstring = ""
            for im ,m in enumerate(matches):
                letter = None
                sub_letter = None
                if m[0] != '' and m[1] != '':
                    digit = m[0]
                    prev_letter = None
                    letter = m[1]
                    recstring = f"\n({m[0]})({m[1]})"
                if m[2] != '':
                    digit = m[2]
                    prev_letter = None
                    recstring = f"\n({m[2]})"
                    
                if m[3] != '':
                    recstring = f"\n({m[3]})"
                    if m[3] == 'a':
                        letter = m[3]
                        prev_letter = None 
                        
                    if prev_letter != None:
                        if len(m[3]) > 1 or m[3] == 'x' or m[3] == 'v':
                            if len(prev_letter) > 1 or prev_letter == 'x' or prev_letter == 'i' or prev_letter == 'v':
                                letter = m[3]
                            else:
                                sub_letter = m[3]
                        else:
                            i_pl = lettres.find(prev_letter)
                            i_l = lettres.find(m[3])
                            if i_pl+1 == i_l:
                                letter = m[3]
                            else:
                                sub_letter = m[3]
                    else:
                        letter = m[3]
                
                if letter != None:
                    prev_letter = letter
                if digit != None:
                    prev_digit = digit
                # print(digit,prev_letter,sub_letter)
                
                # separer chaque partie de la chaine de caractère "(1)(a) ..... (b)  ... (i)  ... (ii) "
                # print(recstring, para.find(recstring))
                text_c = ""
                if prev_m is not None:
                    i_prev = para.find(prev_m)  + len(prev_m)
                    i_cur = para.find(recstring)
                    # print(para,recstring,i_prev,i_cur)
                    
                    sub_para = para[i_prev:i_cur]
                    content[-1]["text"] = sub_para
                else:
                    i_cur = para.find(recstring)
                    text_c = para[0:i_cur]
                    aaa = text_c.replace('\n',' ').strip()
                    if aaa != '' :
                        id_c = f"{id}_pre"
                        if len(content) == 0:
                            content.append({"id":id_c,"text":aaa})
                        else:
                            content[-1]["text"] += " " + aaa
                            
                    
                    
                prev_m = recstring
                
                
                id_c = f"{id}"
                
                # print(digit,prev_letter,sub_letter,text_c)
                if digit is None and prev_letter is None:
                    id_c = f"{id}_pre"
                    content.append({"id":id_c,"text":text_c})
                    continue
                elif digit is not None and prev_letter is None and sub_letter is None:
                    id_c = f"{id}_{digit}"
                    content.append({"id":id_c,"text":text_c})
                    continue
                elif digit is not None and prev_letter is not None and sub_letter is None:
                    id_c = f"{id}_{digit}_{prev_letter}"
                    content.append({"id":id_c,"text":text_c})
                    continue
                elif digit is not None and prev_letter is not None and sub_letter is not None:
                    id_c = f"{id}_{digit}_{prev_letter}_{sub_letter}"
                    content.append({"id":id_c,"text":text_c})
                    continue
                elif digit is None and prev_letter is not None:
                    id_c = f"{id}_{prev_letter}"
                    content.append({"id":id_c,"text":text_c})
                    continue
                else: 
                    print("ya un probleme",id_c)
            
            if prev_m is not None:
                i_prev = para.find(prev_m) + len(prev_m)
                i_cur = len(para) - 1
                
                sub_para = para[i_prev:i_cur]
                # print(content[-1]["id"])
                content[-1]["text"] = sub_para
            else:
                content[-1]["text"] = para
                # print(content[-1]["id"])
                
                    
                
                    
            
            # print(para[:10]," | ",matches)
            
            # content.append(matches)
            
            # content.append({"id":id_c,"text":para.replace("\n"," ").strip()})
     
        
    if id is not None:
        articles.append({"id":id,"title":title,"chapter":chapter,"content":content})
        
    text.extend(articles)

    return text




def extract_rules_from_pdf(pdf_path, start_page, end_page):
    """Extrait le texte d'un fichier PDF entre les pages start_page et end_page (inclus)."""
    doc = fitz.open(pdf_path)
    text = []

    articles = []
    chapter = None
    content = []
    id = None
    title = None
    prev_letter = None
    digit = None
    for page_num in range(start_page - 1, end_page):
        # print(doc[page_num].get_text("blocks"))
        c_page= [
            e[4] for e in doc[page_num].get_text("blocks")
        ]
        for ic,para in enumerate(c_page[2:]):
            if "Editor’s Note" in para:
                continue
            
            if para.upper() == para:
                tmp = para.replace("\n","").strip()
                if tmp != "":
                    chapter = tmp
                    print(chapter)
                continue
            
            match = re.match(r"^Rule (\d+[a-z]*)\s*\n",para,re.MULTILINE)
            if match:
                if id is not None:
                    articles.append({"id":id,"title":title,"chapter":chapter,"content":content})
                content = []
                prev_letter = None
                digit = None
                print(match.group(1))
                id = f"WIPO_R{match.group(1)}"
                title = para.replace("\n","").strip()
                continue

            
            
            
            # if id != "WIPO_A2":
            #     continue   
            # print(para)
                                                           # \d+[a-z]*\.(\d+)
            # matches = re.findall(r"\n\((\d+)\)\(([a-z]+)\)|\n\((\d+)\)|\n\(([a-z]+)\)",para,re.MULTILINE)
            
            # if len(matches) == 0 and len(content) > 0:
            #     content[-1]["text"] += " " + para
            #     continue
            # elif len(matches) == 0 and len(content) < 1: 
            #     id_c = f"{id}_pre"
            #     # print(para)
            #     # return []
            #     content.append({"id":id_c,"text":para }) # .replace("\n"," ").strip()})
                
            # prev_m = None
            # recstring = ""
            # for im ,m in enumerate(matches):
            #     letter = None
            #     sub_letter = None
            #     if m[0] != '' and m[1] != '':
            #         digit = m[0]
            #         prev_letter = None
            #         letter = m[1]
            #         recstring = f"\n({m[0]})({m[1]})"
            #     if m[2] != '':
            #         print("aaa")
            #         return []
            #         digit = m[2]
            #         prev_letter = None
            #         recstring = f"\n({m[2]})"
                    
            #     if m[3] != '':
            #         recstring = f"\n({m[3]})"
            #         if m[3] == 'a':
            #             letter = m[3]
            #             prev_letter = None 
                        
            #         if prev_letter != None:
            #             if len(m[3]) > 1 or m[3] == 'x' or m[3] == 'v':
            #                 if len(prev_letter) > 1 or prev_letter == 'x' or prev_letter == 'i' or prev_letter == 'v':
            #                     letter = m[3]
            #                 else:
            #                     sub_letter = m[3]
            #             else:
            #                 i_pl = lettres.find(prev_letter)
            #                 i_l = lettres.find(m[3])
            #                 if i_pl+1 == i_l:
            #                     letter = m[3]
            #                 else:
            #                     sub_letter = m[3]
            #         else:
            #             letter = m[3]
                
            #     if letter != None:
            #         prev_letter = letter
            #     if digit != None:
            #         prev_digit = digit
            #     # print(digit,prev_letter,sub_letter)
                
            #     # separer chaque partie de la chaine de caractère "(1)(a) ..... (b)  ... (i)  ... (ii) "
            #     # print(recstring, para.find(recstring))
            #     text_c = ""
            #     if prev_m is not None:
            #         i_prev = para.find(prev_m)  + len(prev_m)
            #         i_cur = para.find(recstring)
            #         # print(para,recstring,i_prev,i_cur)
                    
            #         sub_para = para[i_prev:i_cur]
            #         content[-1]["text"] = sub_para
            #     else:
            #         i_cur = para.find(recstring)
            #         text_c = para[0:i_cur]
            #         aaa = text_c.replace('\n',' ').strip()
            #         if aaa != '' :
            #             id_c = f"{id}_pre"
            #             if len(content) == 0:
            #                 content.append({"id":id_c,"text":aaa})
            #             else:
            #                 content[-1]["text"] += " " + aaa
                            
                    
                    
            #     prev_m = recstring
                
                
                # id_c = f"{id}"
                
            #     # print(digit,prev_letter,sub_letter,text_c)
            #     if digit is None and prev_letter is None:
            #         id_c = f"{id}_pre"
            #         content.append({"id":id_c,"text":text_c})
            #         continue
            #     elif digit is not None and prev_letter is None and sub_letter is None:
            #         id_c = f"{id}_{digit}"
            #         content.append({"id":id_c,"text":text_c})
            #         continue
            #     elif digit is not None and prev_letter is not None and sub_letter is None:
            #         id_c = f"{id}_{digit}_{prev_letter}"
            #         content.append({"id":id_c,"text":text_c})
            #         continue
            #     elif digit is not None and prev_letter is not None and sub_letter is not None:
            #         id_c = f"{id}_{digit}_{prev_letter}_{sub_letter}"
            #         content.append({"id":id_c,"text":text_c})
            #         continue
            #     elif digit is None and prev_letter is not None:
            #         id_c = f"{id}_{prev_letter}"
            #         content.append({"id":id_c,"text":text_c})
            #         continue
            #     else: 
            #         print("ya un probleme",id_c)
            
            # if prev_m is not None:
            #     i_prev = para.find(prev_m) + len(prev_m)
            #     i_cur = len(para) - 1
                
            #     sub_para = para[i_prev:i_cur]
            #     # print(content[-1]["id"])
            #     content[-1]["text"] = sub_para
            # else:
            #     content[-1]["text"] = para
            #     # print(content[-1]["id"])
                
                    
                
                    
            
            # print(para[:10]," | ",matches)
            
            # content.append(matches)
            if len(content) > 0:
                content[-1]["text"] += para
            else:
                content.append({"id":id,"text":para})
     
        
    if id is not None:
        articles.append({"id":id,"title":title,"chapter":chapter,"content":content})
        
    text.extend(articles)

    return text




path_file = "./data_raw/Official Legal Publications/2-PCT_wipo-pub-274-2024-en-patent-cooperation-treaty.pdf"

# articles
# output_file = "articles_WIPO.json"
# start_page = 9
# end_page =  54
# data = extract_articles_from_pdf(path_file, start_page, end_page)

#rules
output_file = "rules_WIPO.json"
start_page = 73
end_page =  236
data = extract_rules_from_pdf(path_file, start_page, end_page)




with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
