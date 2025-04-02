import requests
 
prefix = "https://www.msgg.gov.mr"

def download_file(url):
    html = ""
    try:
        r = requests.get(url)
        # print(r.text[:100])
        html = r.text
    except:
        pass
    return html

def reformat_date_string_as_iso(lDate):
    return lDate[:10]

gErrors = [('%29', ""),
           ('..', "."),
           ('207.pdf', "2017.pdf"),
           ('209.pdf', "2019.pdf"),
           ('2018fin.pdf', "2018.pdf")
           ]


def get_doc_type_field_info(lLines):
    lLines2 = [x for x in lLines  if '<body class="path-node page-node-type-journal-officiel"' in x]
    if(len(lLines2) == 0):
        return False
    return True

def get_date_field_info(lLines):
    lLines2 = [x for x in lLines  if '<time datetime="' in x]
    if(len(lLines2) == 0):
        return None
    lDate = lLines2[0].split(" ")[1]
    print("PARSER_DATE_FIELD", lDate)
    lDate = lDate.replace('datetime="', "")
    return reformat_date_string_as_iso(lDate)

def get_jo_number_info(lLines):
    lNumero = None
    for (i, x) in enumerate(lLines):
        if('div class="field field--name-field-numero' in x):
            y = lLines[i + 1]
            # example : ...<div class="field__item">1442</div>
            y1 = y.replace("<", "[")
            y1 = y1.replace(">", "[").split("[")
            print("PARSER_ISSUE_NUMBER_FIELD", y1[6])            
            lNumero = y1[6]
    return lNumero

def normalize_names(num, lang, lNumero, lDate, lFiles1):
    lFiles = []
    for f1 in lFiles1:
        toks = f1.split(" ")
        for p in toks:
            if('href="https://' in p):
                p1 = p.replace('href="', "")
                p2 = p1.replace('"', "")                
                lFiles.append((lang, num, lNumero, lDate, p2))
    return lFiles

def download_jo(num, lang):
    name = prefix + "/" + lang + "/node/" + str(num)
    print(("DOWNLOADING_FILE", name))
    lText = download_file(name)
    lFiles = []
    lLines = lText.split("\n")
    l_IS_JO = get_doc_type_field_info(lLines)
    if(not l_IS_JO):
        print("PDF_NAME_PARSING_ERROR_NOT_JO", name)
        return []    
    lDate = get_date_field_info(lLines)
    lNumero = get_jo_number_info(lLines)
    lFiles1 = [x for x in lLines if ('href="https://' in x and "pdf" in x)]
    lFiles = []
    try:
        lFiles = normalize_names(num, lang, lNumero, lDate, lFiles1)
    except:
        print("PDF_NAME_PARSING_ERROR", lFiles1)
        raise
        
    print("PDF_RESULT", lFiles)
    return lFiles

def save_pdf_dry_run(metadata):
    (lang, num, lNum, lDate, url) = metadata
    print(("SAVING_PDF_FILE", metadata))
    y = lDate.split("-")[0]
    lDir = "data/" + lang + "/" + y    
    new_name = lDir + "/JO_" + lDate + "_" + lNum + ".pdf"
    lCSVLine = "\t".join([str(x) for x in metadata]) + "\t" + new_name
    print("SAVING_PDF_FILE_CSV\t" + lCSVLine)
    
def save_pdf(metadata):
    (lang, num, lNum, lDate, url) = metadata
    print(("SAVING_PDF_FILE", metadata))
    y = lDate.split("-")[0]
    lDir = "data/" + lang + "/" + y
    new_name = lDir + "/JO_" + lDate + "_" + lNum + ".pdf"
    response = requests.get(url)
    import os
    if not os.path.exists(lDir):
        os.makedirs(lDir)
    if response.status_code == 200:
        with open(new_name, 'wb') as file:
            file.write(response.content)
            print(("SAVING_PDF_FILE_OK", new_name))
    else:
        print(("SAVING_PDF_FAILED", metadata))
        pass # fail silently
    
def download_all(min_num = 32, max_num = 34):
    for number in range(min_num, max_num + 1):
        for lang in ["ar", "fr"]:
            lFiles = download_jo(number, lang)
            for f in lFiles :
                save_pdf(f)

# download_all(0, 2000)
download_all(1000, 1015)
