# Flask Setup
import os
from flask import Flask, jsonify, request, abort, render_template

app = Flask(__name__)
# Google Sheets API Setup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

credential = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ],
)
client = gspread.authorize(credential)
gsheet = client.open("Crud Test Table").sheet1


def get_data_from_table():
    headers = []
    table = gsheet.get_all_values()
    headers = table[0]
    # data = table[1:]

    data = []
    for item in table[1:]:

        tmp_arr = []
        for k in item:
            if k.isdigit():

                tmp_arr.append(int(k))
            elif k == "":
                tmp_arr.append(0)
            else:
                tmp_arr.append(k)
        data.append(tmp_arr)
    return headers, data


# An example GET Route to get all reviews
@app.route("/warehouse", methods=["GET", "POST"])
def all_reviews():
    # return gsheet.get_all_values()
    # return render_template("index.html", formList=jsonify(gsheet.get_all_records()))
    if request.method == "POST":
        print("pressed submit", request.form)
        form_data = request.form.getlist("quantity")
        updated_data = []

        row = []
        counter = 0
        for item in form_data:

            row.append(int(item))
            counter += 1
            if counter == 4:
                counter = 0
                updated_data.append(row)
                row = []

        print(updated_data)
        gsheet.update("B2:E1000", updated_data)

    # print("request = ", request.args)

    headers, data = get_data_from_table()

    return render_template("index.html", headers=headers, data=data)


# An example POST Route to add a review
@app.route("/add_review", methods=["POST"])
def add_review():
    req = request.get_json()
    row = [req["email"], req["date"], req["score"]]
    gsheet.insert_row(row, 2)  # since the first row is our title header
    return jsonify(gsheet.get_all_records())


# An example DELETE Route to delete a review
@app.route("/del_review/<email>", methods=["DELETE"])
def del_review(email):
    cells = gsheet.findall(str(email))
    for c in cells:
        gsheet.delete_row(c.row)
    return jsonify(gsheet.get_all_records())


# An example PATCH Route to update a review
@app.route("/update_review", methods=["PATCH"])
def update_review():
    req = request.get_json()
    cells = gsheet.findall(req["email"])
    for c in cells:
        gsheet.update_cell(c.row, 3, req["score"])
    return jsonify(gsheet.get_all_records())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # from waitress import serve

    # serve(app, host="0.0.0.0", port=5000)
    app.run(debug=True, host="0.0.0.0", port=port)
