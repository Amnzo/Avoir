from io import BytesIO
from PyPDF2 import PdfReader
from django.http import HttpResponse
from django.shortcuts import render


def extract_commands(content):
    content.replace('"Certaines données personnelles sensibles de vos clients',"")
    commands=content.split("BL")
    return commands
def decortiquer_bl(bl_content):
    produit1=produit2=option=None
    bl_lines=bl_content.split('\n')
    
    numero_bl=bl_lines[0].split("du")[0] 
    date=bl_lines[0].split("du")[1].split('Réf')[0]#Réf
    porteur=bl_lines[0].split("du")[1].split('Réf')[1]#Réf
    
    print("")
    print("----------------------")
    print(numero_bl)
    produit1=bl_lines[1]
    print(f" Produit 1  {produit1}")
    second_line=bl_lines[2].split()
    print(len(second_line))
    if len(second_line)>5 :
        produit2=bl_lines[2]
       
    else :
        option=bl_lines[2]
       
    if len(bl_lines)>3 :
        option=bl_lines[3]
    print(f" Produit 2  {produit2}")
    print(f" Option  {option}")
    return numero_bl,produit1,produit2,option,date,porteur
    

    
    #if len
    #print(f"{produit2}")
    #print(f"{option}")
    #print("")
    #print("")
    index=1
    # for l in bl_lines:
    #     index=index+1
    #     if l.startswith("Powered by TCPDF"):
    #         pass
    #     else :
    #         pass

           # print(f"{index}***-{l}")

    
    

def nova(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']
        pdf_data = pdf_file.read()
      
        pdf_buffer = BytesIO(pdf_data)
        pdf_reader = PdfReader(pdf_buffer)
        content = ""
        for page_num in range(0,len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            encoded_text = text.encode('utf-8', 'ignore')  # Ignore characters that cannot be encoded
            decoded_text = encoded_text.decode('utf-8')
            content += decoded_text
        #print(content)
        formatted_commands = []
        content.replace('"Certaines données personnelles sensibles de vos clients',"")
        bls = extract_commands(content)
        for bl in bls:
            lines = bl.split('\n')
            if "Certaines données personnelles sensibles" in bl.split('\n')[0] :
                pass
            else:
                numero_bl,produit1,produit2,option,date,porteur=decortiquer_bl(bl)
                formatted_command = {
                "BL": numero_bl,
                "Date": date,
                "Porteur": porteur.replace(" Prix Facturé H.T.", ""),
                "Produit1": ' '.join(produit1.split()[1:]) if produit1 and len(produit1.split()) > 1 else None,
                "Produit2": ' '.join(produit2.split()[1:]) if produit2 and len(produit2.split()) > 1 else None,
                 "Option": ' '.join(option.split()[1:]) if option and len(option.split()) > 1 else None
            }

                formatted_commands.append(formatted_command)
            print(formatted_commands)
        return render(request, 'excel/nova.html', {'formatted_commands': formatted_commands})
                
                
                
    return render(request,'excel/nova.html')