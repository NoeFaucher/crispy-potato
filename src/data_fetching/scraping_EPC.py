from bs4 import BeautifulSoup
import requests
import json
import re

# x = requests.get('https://www.epo.org/en/legal/epc/2020/a119.html')
# print(x.contentea

i = 1
keep_going = True
rules = []
ilettre = -1
lettres = "abcdefghijklmnopqrstuvwxyz"
while i < 179:
    lettre = "" if ilettre == -1 else lettres[ilettre]
    # x = requests.get(f"https://www.epo.org/en/legal/epc/2020/r{i}{lettre}.html")
    x = requests.get(f"https://www.epo.org/en/legal/epc/2020/f2.html")

    keep_going = (x.status_code == 200)
    if not keep_going:
        ilettre = -1
        i+=1
        continue
    
    ilettre+=1
    soup = BeautifulSoup(x.content, 'html.parser')
    tittle = soup.find('h1', attrs={'class':'h2'})
    data_html = tittle.find_parent('div',attrs={'data-region':'second'})
    
    rules.append(str(data_html))
    break

json.dump(rules,open("rules_fee.json","w"),indent=4)

all_data = json.load(open("rules_fee.json",'r'))
print(len(all_data))

# res_data = []
# for i,text in enumerate(all_data):

#     soup = BeautifulSoup(text, 'html.parser')
    
#     title = soup.find('h1', class_='h2')
    
#     index = len(title.contents)- 1
#     for cont in reversed(title.contents):
#         if "<" not in str(cont) and "google" not in str(cont):
#             title.contents[index].replace_with(f"{title.contents[index]}")
#             break
#         index -= 1
#     for footnote in title.find_all('a', class_='FootnoteRef'):
#         footnote_number = footnote.find('sup').text
#         new_footnote_text = f' [{footnote_number}]'
#         footnote.replace_with(new_footnote_text)
    
#     footnotes = []
#     footnotes_div = soup.find('div', class_='DOC4NET2-notes')

#     if footnotes_div:
#         for p in footnotes_div.find_all('p'):
#             key = p.find('sup')
#             if key :
#                 key = key.get_text(strip=False)
#                 text = p.get_text(strip=False).replace(key, "").strip()
#                 footnotes.append({"key": key, "content": text})
            
            
#     title = title.get_text() if title else ""
    
    
#     # Extract the main content
#     content = []
#     content_div = soup.find('div', class_='epolegal-content')
#     id = None
#     title_a = title
#     footnote_d = []
#     if content_div:
#         prev_number = None
#         for j,element in enumerate(content_div.children):
#             if element.name == 'p':
#                 if "class" in element.attrs and "bold" in element.attrs["class"] and ("Article" in element.get_text(" ") or True):
                    
#                     id_a = "TRANSITIONALPROVISIONS"
                    
#                     match = re.match(r"Article\s+(\d+[a-z]*)", title_a)
#                     anumb = None
#                     if match:
#                         # Extraire le nombre
#                         anumb = match.group(1)
#                         id_a = f"{id_a}_A{anumb}"
                        
#                     match = re.match(r"Section\s+([A-Z]+[a-z]*)", title_a)
#                     anumb = None
#                     if match:
#                         # Extraire le nombre
#                         anumb = match.group(1)
#                         id_a = f"{id_a}_S{anumb}"
                        
                        
#                     data = {
#                         "id": id_a,
#                         "title": title_a,
#                         "content": content,
#                         "footnotes": footnote_d
#                     }
#                     content = []
#                     footnote_d = []
#                     res_data.append(data)
#                     for footnote in element.find_all('a', class_='FootnoteRef'):
#                         footnote_number = footnote.find('sup').text
#                         new_footnote_text = f' [{footnote_number}]'
#                         footnote.replace_with(new_footnote_text)
#                         index_f = None
#                         for index_f_t, v_f in enumerate(footnotes):
#                             if v_f["key"] == footnote_number:
#                                 footnote_d.append(v_f)
#                                 break
#                     title_a = element.get_text(" ")
#                 else:
#                     for footnote in element.find_all('a', class_='FootnoteRef'):
#                         footnote_number = footnote.find('sup')
#                         if footnote_number:
#                             footnote_number = footnote_number.text
#                             new_footnote_text = f' [{footnote_number}]'
#                             footnote.replace_with(new_footnote_text)
#                             index_f = None
#                             for index_f_t, v_f in enumerate(footnotes):
#                                 if v_f["key"] == footnote_number:
#                                     footnote_d.append(v_f)
#                                     break
#                         else:
#                             # print(j," ",footnote)
#                             pass
#                     content.append(element.get_text(" "))
        
#         id_a = "TRANSITIONALPROVISIONS"
        
#         match = re.match(r"Article\s+(\d+[a-z]*)", title_a)
#         anumb = None
#         if match:
#             # Extraire le nombre
#             anumb = match.group(1)
#             id_a = f"{id_a}_A{anumb}"
#         match = re.match(r"Section\s+([A-Z]+[a-z]*)", title_a)
#         anumb = None
#         if match:
#             # Extraire le nombre
#             anumb = match.group(1)
#             id_a = f"{id_a}_S{anumb}"
            
#         data = {
#             "id": id_a,
#             "title": title_a,
#             "content": content,
#             "footnotes": footnote_d
#         }
#         res_data.append(data)
# json.dump(res_data, open("formated_transitionalprovisions.json","w") ,indent=4, ensure_ascii=False)
            
res_data = []
for i,text in enumerate(all_data):
    # if i != 19 - 1:
    #     continue

    soup = BeautifulSoup(text, 'html.parser')

    title = soup.find('h1', class_='h2')
    
    index = len(title.contents)- 1
    for cont in reversed(title.contents):
        if "<" not in str(cont) and "google" not in str(cont):
            title.contents[index].replace_with(f" - {title.contents[index]}")
            break
        index -= 1
    
    # print(title.contents)
    
    for footnote in title.find_all('a', class_='FootnoteRef'):
        footnote_number = footnote.find('sup').text
        new_footnote_text = f' [{footnote_number}]'
        footnote.replace_with(new_footnote_text)
    
        
        

    footnotes = []
    footnotes_div = soup.find('div', class_='DOC4NET2-notes')

    if footnotes_div:
        for p in footnotes_div.find_all('p'):
            key = p.find('sup').get_text(strip=False)
            text = p.get_text(strip=False).replace(key, "").strip()
            footnotes.append({"key": key, "content": text})

    title = title.get_text() if title else ""
    

    # Extract the main content
    content = []
    content_div = soup.find('div', class_='epolegal-content')
    id = None
    if content_div:
        id = content_div.attrs["id"]
        prev_number = None
        for j,element in enumerate(content_div.children):
            if element.name == 'p':
                a_id = element.find_next('a')
                if a_id == None or "id" not in a_id.attrs:
                    a_id = None
                else:
                    a_id = a_id.attrs["id"]
                    
                if a_id is not None and not a_id.startswith(id):
                    a_id = None
                    
                    
                for footnote in element.find_all('a', class_='FootnoteRef'):
                    footnote_number = footnote.find('sup').text
                    new_footnote_text = f' [{footnote_number}] '
                    footnote.replace_with(new_footnote_text)
                    
                text = element.get_text(strip=False)
                
                
                # recuperer le nombre entre parenthese et suprimer le de la chaine de caractere
                match = re.match(r"\((\d+)\)", text)
                nombre = None
                if match:
                    # Extraire le nombre
                    nombre = match.group(1)
                    # Supprimer le nombre et les parenthèses de la chaîne
                    text = text[len(match.group(0)):].strip()
                    prev_number = nombre

                match = re.match(r"\(([a-z])\)", text)
                lettre = None
                if match:
                    # Extraire le nombre
                    lettre = match.group(1)
                    # Supprimer le nombre et les parenthèses de la chaîne
                    text = text[len(match.group(0)):].strip()


                if a_id is None and prev_number is not None and lettre is None:
                    a_id = f"{id}_{prev_number}"
                if a_id is None and prev_number is not None and lettre is not None:
                    a_id = f"{id}_{prev_number}_{lettre}"
               
               
                
                if lettre is None and nombre is None and prev_number is not None:
                    a_id = f"{id}_{prev_number}_inter"
                elif lettre is None and nombre is None:
                    a_id = f"{id}_pre"
                
                
                content.append({"text": text, "id": a_id  })


    

    data = {
        "id": id,
        "title": title,
        "content": content,
        "footnotes": footnotes
    }
    
    res_data.append(data)




json.dump(res_data, open("f2.json","w") ,indent=4, ensure_ascii=False)




# links = title.find_all("a")
# for l in links:
#     if "id" in l.attrs and l.attrs["id"].startswith("reg.f"):
#         l.replace_with("[aaa]")
#         print(l)


# print(title.text)



