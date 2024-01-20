

Bonsoir, quand vous aurez le temps, merci de visiter ce lien pour voir ce qui a été fait.

https://karimatoka.pythonanywhere.com/bl/

------espace admin -----
login :   amnzo
pwd :    123456

--------simple user------ : 
login :  salmi
pwd   :  Salmi@Ensa123

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bon de Commande</title>
    <!-- Add any additional styles or meta tags needed for your page -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body class="container-fluid">
    <div style="display: flex; justify-content: space-between;">
        <!-- Left Top: Store Info Card -->
        <div style="width: 48%;">
            <div class="card">
                <div class="card-body">
                    {{ bon_commande }}
                    <h5 class="card-title">Your Store Name</h5>
                    <p class="card-text">123 Store Street, City</p>
                    <p class="card-text">Phone: (123) 456-7890</p>
                </div>
            </div>
        </div>
    
        <!-- Right Top: Second Store Info Card -->
        <div style="width: 48%;">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Your Store Name</h5>
                    <p class="card-text">123 Store Street, City</p>
                    <p class="card-text">Phone: (123) 456-7890</p>
                </div>
            </div>
        </div>
    </div>
    
    

    <!-- Main Content: Bon de Commande Table -->
    <h1 class="mt-4">Bon de Commande</h1>
    <table class="table">
        <tr>
            <th>Reference</th>
            <th>Designation</th>
            <th>Sphere</th>
            <th>Cylindre</th>
            <th>Axe</th>
            <th>OEIL</th>
            <th>Qte</th>
        </tr>
        <tr>
            <td>{{bon_commande.produit_d.id}}</td>
            <td>{{bon_commande.produit_d.nom}}</td>
            <td>{{bon_commande.sphere_d}}</td>
            <td>{{bon_commande.cylindre_d}}</td>
            <td>{{bon_commande.axe_d}}</td>
            <td>DROIT</td>

            <td>{{bon_commande.quatite_d}}</td>
        </tr>
        <tr>
            <td>{{bon_commande.produit_g.id}}</td>
            <td>{{bon_commande.produit_g.nom}}</td>
            <td>{{bon_commande.sphere_g}}</td>
            <td>{{bon_commande.cylindre_g}}</td>
            <td>{{bon_commande.axe_g}}</td>
            <td>GAUCHE</td>
            <td>{{bon_commande.quatite_g}}</td>
        </tr>
        
        <!-- Add more rows for other products with dummy data -->
    </table>

    <!-- Add any additional content or styling needed for your page -->

    <!-- Bootstrap Scripts -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>
</html>





def generate_pdf(request, bon_commande_id):
    # Retrieve the Bon_Commande instance
    bon_commande = Bon_Commande.objects.get(id=bon_commande_id)

    # Create an HttpResponse object with the content type 'application/pdf'
    response = HttpResponse(content_type='application/pdf')
    # Set the content disposition header to specify the filename as "example.pdf"
    response['Content-Disposition'] = f'filename="{bon_commande.id}_bon_commande.pdf"'

    # Create a PDF document
    pdf_doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Store Information Card
    store_card_content = f"""
    Your Store Name
    123 Store Street, City
    Phone: (123) 456-7890
    """
    store_card = get_info_card(store_card_content)
    elements.extend(store_card)

    # Client Information Card (dummy data)
    client_card_content = f"""
    Client Name: {bon_commande.client.nom}
    Client Address: {bon_commande.client.prenom}
    Client Phone: {bon_commande.client.nom}
    """
    client_card = get_info_card(client_card_content)
    elements.extend(client_card)

    # Table data
    data = [
        ["ID", "Nom", "Sphere", "Cylindre", "Axe", "OEIL", "Quantité"],
        [bon_commande.produit_d.id, bon_commande.produit_d.nom, bon_commande.sphere_d,
         bon_commande.cylindre_d, bon_commande.axe_d, "DROIT", bon_commande.quatite_d],
        [bon_commande.produit_g.id, bon_commande.produit_g.nom, bon_commande.sphere_g,
         bon_commande.cylindre_g, bon_commande.axe_g, "GAUCHE", bon_commande.quatite_g],
    ]

    # Create a table and add it to the elements list
    table = Table(data, colWidths=60, rowHeights=30)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.red),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.yellow),
                               ]))
    elements.append(table)

    # Build the PDF document
    pdf_doc.build(elements)

    # Return the HttpResponse object with the generated PDF
    return response


def get_info_card(content):
    styles = getSampleStyleSheet()
    info_card = [
        Spacer(1, 0),
        Paragraph(content, styles['Normal']),
        Spacer(1, 12),
    ]
    return info_card