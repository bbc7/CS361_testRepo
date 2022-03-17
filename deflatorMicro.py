# NAME: Colin Bebee
# DATE: 2/7/22
# CLASS: CS361
# ASSIGNMENT: Project (microservice element)


from flask import Flask, json, request
import pandas as pd
from flask_cors import CORS


# Load deflation factors (downloaded from BLS website)
deflator = pd.read_csv("deflator.csv")
deflator.set_index("Year", inplace=True)

# Create basic Flask object
api = Flask(__name__)
CORS(api)

# Only using the 'deflation' route handler | no others will be implemented for this microservice.
@api.route('/deflation', methods=['GET'])
def getDeflatedValue():
    desiredYear = str(request.args.get("year"))
    currentYear = 2021

    currentCost = str(request.args.get("cost"))

    # Ensure that the desired year is within the range of CPI data provided by BLS
    if (int(desiredYear) < 2022 and int(desiredYear) > 1913):
        currentYearFactor = deflator.loc[currentYear]["deflatorFactor"]
        desiredYearFactor = deflator.loc[int(desiredYear)]["deflatorFactor"]

        oldCost = round(float(currentCost) * (desiredYearFactor/currentYearFactor), 2)

        returnValues = [{str(desiredYear): str(oldCost), str(currentYear): str(currentCost), "converted": str(oldCost)}]
    else:
        returnValues = [{"converted": "0"}]

    return json.dumps(returnValues)


# MAIN
if __name__ == '__main__':
    api.run(port=5555) 