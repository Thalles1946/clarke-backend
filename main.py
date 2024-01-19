from ariadne import QueryType, graphql_sync, make_executable_schema
from ariadne.explorer import ExplorerGraphiQL
from flask import Flask, jsonify, request
import json

type_defs = """
    type Query {
        consultaEmpresas(kWh:Float!): [Empresa]
    }
    type Empresa {
        nome: String!
        logo: String!
        estado: String!
        custoKWh: Float!
        minimoKWh: Float!
        numeroClientes: Int!
        avaliacao: Float!
    }
"""

query = QueryType()


nome_arquivo = './clarke-api/mock-data.json'

def load_data(kWh):
    try:
        with open(nome_arquivo,'r') as arquivo_json:
            data = json.load(arquivo_json)
        data["data"] = [empresa for empresa in data["data"] if empresa["limite_minimo_kWh"]>= int(kWh)]
        data["data"] = sorted(data["data"], key=lambda x: x["avaliacao_media_clientes"], reverse=True)
        if data["data"] is not None:
            return data["data"]
        else:
            return []    
    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except json.decoder.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"Erro desconhecido: {e}")



@query.field("consultaEmpresas")
def consulta_empresas(_,info,kWh):
    
    try:
        empresas = load_data(kWh)
        return empresas    
    except Exception as e:
        print(f"Function consulta_empresas exception : {e}")

    return "consulta"
    


schema = make_executable_schema(type_defs, query)

app = Flask(__name__)

# Retrieve HTML for the GraphiQL.
# If explorer implements logic dependant on current request,
# change the html(None) call to the html(request)
# and move this line to the graphql_explorer function.
explorer_html = ExplorerGraphiQL().html(None)


@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    # On GET request serve the GraphQL explorer.
    # You don't have to provide the explorer if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL explorer app.
    return explorer_html, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)