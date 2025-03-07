from flask import Flask, render_template, request, redirect, url_for
from azure.cosmos import CosmosClient, PartitionKey
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 📌 Configuración de Cosmos DB
URL = "https://testdbz.documents.azure.com:443/"
KEY = "RBBPJ46PZ8lS4QwrvZ1rfgpIpzePXdXl9gKbPJIyOMKDeezI7uydBOA8h5zVDAN7jfQwoYqrWGppACDb54T9Gw=="
DATABASE_NAME = "MiBaseDeDatos"
CONTAINER_NAME = "MiContenedor"

# Conectar a Cosmos DB
client = CosmosClient(URL, credential=KEY)
database = client.create_database_if_not_exists(id=DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME, partition_key=PartitionKey(path="/id"), offer_throughput=400
)

# 📌 Página principal - Lista de productos
@app.route("/")
def index():
    items = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
    return render_template("index.html", items=items)

# 📌 Agregar un nuevo producto
@app.route("/add", methods=["POST"])
def add_item():
    item_id = request.form["id"]
    nombre = request.form["nombre"]
    precio = float(request.form["precio"])
    stock = int(request.form["stock"])

    item = {"id": item_id, "nombre": nombre, "precio": precio, "stock": stock}
    container.create_item(body=item)

    return redirect(url_for("index"))

# 📌 Editar un producto existente
@app.route("/edit/<string:item_id>", methods=["POST"])
def edit_item(item_id):
    nuevo_precio = float(request.form["precio"])
    item = container.read_item(item=item_id, partition_key=item_id)
    item["precio"] = nuevo_precio
    container.replace_item(item=item_id, body=item)

    return redirect(url_for("index"))

# 📌 Eliminar un producto
@app.route("/delete/<string:item_id>")
def delete_item(item_id):
    container.delete_item(item=item_id, partition_key=item_id)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Obtiene el puerto de Azure o usa 8000 por defecto
    app.run(host="0.0.0.0", port=port, debug=True)
