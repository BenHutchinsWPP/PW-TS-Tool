from pathlib import Path
import win32com.client
import pandas as pd

def chk(SimAutoOutput, Message):
    """
    Function used to catch and display errors passed back from SimAuto

    SimAuto return object format:
    [0] = Error message, if any
    [1+] = Return data
    """

    if SimAutoOutput[0] != '':
        print('Error: ' + SimAutoOutput[0])
        return None
    else:
        print(Message)

    if len(SimAutoOutput) == 1:
        return None
    elif len(SimAutoOutput) == 2:
        return SimAutoOutput[1]
    else:
        return SimAutoOutput[1:]

def IsNumber(value):
    try:
        result = float(value)
        return True
    except:
        return False

def FormatVolt(volt):
    # Round the number to handle floating-point precision issues
    rounded_num = round(volt, 2)
    
    # Check if the rounded number is a whole number and cast to int if true
    if rounded_num.is_integer():
        return f"{int(rounded_num)}"
    else:
        return f"{rounded_num}"

def GetDf(table_get: str, parameters_get: dict[str,type]):
    msg = 'GetParametersMultipleElementRect(' + table_get + ': [' + ', '.join(parameters_get) + '])'
    print(msg)

    rows = chk(SimAuto.GetParametersMultipleElementRect(table_get, list(parameters_get.keys()), ""), msg)
    df = pd.DataFrame(rows)
    df.columns = parameters_get.keys()
    for column, dtype in parameters_get.items():
        df[column] = df[column].astype(dtype)
    return df

def GetBusData():
    table_get = 'Bus'
    parameters_get = {
        'BusNum': int
        ,'BusName': str
        ,'BusNomVolt': float
        ,'Vpu': float
        ,'AreaNum': int
        ,'ZoneNum': int
        ,'OwnerNum': int
        ,'DataMaintainer': str
    }
    df = GetDf(table_get, parameters_get)
    df['key'] = df['BusNum']
    return df

def GetGenData():
    table_get = 'Gen'
    parameters_get = {
        'BusNum': int
        ,'BusName': str
        ,'NomkV': float
        ,'ID': str
        ,'Status': str
        ,'Vpu': float
        ,'RegBusNum': int
        ,'VoltSet': float
        ,'RegBusVpu': float
        ,'MW': float
        ,'MWMin': float
        ,'MWMax': float
        ,'EnforceMWLimit': str
        ,'AGC': str
        ,'Mvar': float
        ,'MvarMin': float
        ,'MvarMax': float
        ,'AVR': str
        ,'AllLabels': str
        ,'RegBusNum': float
    }
    df = GetDf(table_get, parameters_get)
    df['key'] = df['BusNum'].astype(str) + '_' + df['ID']
    return df

def GetMsc1Data():
    table_get = 'SwitchedShuntModel_MSC1'
    parameters_get = {
        'BusNum': int
        ,'ID': str
        ,'Status': str
        ,'Tin1': float
        ,'Vmin1': float
        ,'Tout1': float
        ,'Vmax1': float
        ,'Tin2': float
        ,'Vmin2': float
        ,'Tout2': float
        ,'Vmax2': float
        ,'Tlck': float
    }
    df = GetDf(table_get, parameters_get)
    df['key'] = df['BusNum'].astype(str) + '_' + df['ID']
    return df

def GetMsr1Data():
    table_get = 'SwitchedShuntModel_MSR1'
    parameters_get = {
        'BusNum': int
        ,'ID': str
        ,'Status': str
        ,'Tin1': float
        ,'Vmax1': float
        ,'Tout1': float
        ,'Vmin1': float
        ,'Tin2': float
        ,'Vmax2': float
        ,'Tout2': float
        ,'Vmin2': float
    }
    df = GetDf(table_get, parameters_get)
    df['key'] = df['BusNum'].astype(str) + '_' + df['ID']
    return df

def GetLhvrtData():
    table_get = 'RelayModel_LHVRT'
    parameters_get = {
        'BusNum': int
        ,'ID': str
        ,'Status': str
        ,'Vref': float
        ,'dvtrp1': float
        ,'dvtrp2': float
        ,'dvtrp3': float
        ,'dvtrp4': float
        ,'dvtrp5': float
        ,'dvtrp6': float
        ,'dvtrp7': float
        ,'dvtrp8': float
        ,'dvtrp9': float
        ,'dvtrp10': float
        ,'dttrp1': float
        ,'dttrp2': float
        ,'dttrp3': float
        ,'dttrp4': float
        ,'dttrp5': float
        ,'dttrp6': float
        ,'dttrp7': float
        ,'dttrp8': float
        ,'dttrp9': float
        ,'dttrp10': float
        ,'Alarm': int
    }
    df = GetDf(table_get, parameters_get)
    df['key'] = df['BusNum'].astype(str) + '_' + df['ID']
    return df

def CheckTSLogic():
    # Initialize the data check DataFrame
    dfCheckcolumns = {
        'BusNum': int
        ,'BusName': str
        ,'NomkV': float
        ,'ID': str
        ,'Message': str
        ,'Timer': float # If applicable, how long until the logic activates
    }
    dfCheck = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in dfCheckcolumns.items()})

    # Get tables for relevant objects
    dfBus = GetBusData()
    dfGen = GetGenData()
    dfMsc1 = GetMsc1Data()
    dfMsr1 = GetMsc1Data()
    dfLhvrt = GetLhvrtData()

    # Get relevant shunt data for MSC1 MSR1 checks. 
    table_get = 'Shunt'
    parameters_get = {
        'BusNum': int
        ,'BusName': str
        ,'ID': str
        ,'MvarNom': float
    }
    dfShunt = GetDf(table_get, parameters_get)
    dfShunt['key'] = dfShunt['BusNum'].astype(str) + '_' + dfShunt['ID']

    # ------------- Check if MSC1 models will activate. -------------
    dfMsc1Bus = pd.merge(dfMsc1, dfBus[['BusNum','BusName','BusNomVolt','Vpu']], how='left', on='BusNum')
    dfMsc1BusShunt = pd.merge(dfMsc1Bus, dfShunt[['key','MvarNom']], how='left', on='key')

    for index, row in dfMsc1BusShunt.iterrows():
        # Keys for this row
        checkResult = {
            'BusNum': row['BusNum']
            ,'BusName': row['BusName']
            ,'NomkV': row['BusNomVolt']
            ,'ID': row['ID']
            ,'Value':row['Vpu']
            ,'Limit':0.0
            ,'Timer': 0.0
            ,'Message': ''
        }

        # Check logic.
        if(row['MvarNom'] == 0):
            # Shunt out of service. Could be switched in-service. 
            if(row['Vpu'] < row['Vmin1']):
                checkResult.update({
                    'Message': 'MSC1 Activation on Vmin1'
                    ,'Limit': row['Vmin1']
                    ,'Timer': row['Tin1']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)
            if(row['Vpu'] < row['Vmin2']):
                checkResult.update({
                    'Message': 'MSC1 Activation on Vmin2'
                    ,'Limit': row['Vmin2']
                    ,'Timer': row['Tin2']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)
        else:
            # Shunt in service. Could be switched out of service.
            if(row['Vpu'] > row['Vmax1']):
                checkResult.update({
                    'Message': 'MSC1 Activation on Vmax1'
                    ,'Limit': row['Vmax1']
                    ,'Timer': row['Tout1']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)
            if(row['Vpu'] > row['Vmax2']):
                checkResult.update({
                    'Message': 'MSC1 Activation on Vmax2'
                    ,'Limit': row['Vmax2']
                    ,'Timer': row['Tout2']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)

    # ------------- Check if MSR1 models will activate. -------------
    dfMsr1Bus = pd.merge(dfMsr1, dfBus[['BusNum','BusName','BusNomVolt','Vpu']], how='left', on='BusNum')
    dfMsr1BusShunt = pd.merge(dfMsr1Bus, dfShunt[['key','MvarNom']], how='left', on='key')

    for index, row in dfMsr1BusShunt.iterrows():
        # Keys for this row
        checkResult = {
            'BusNum': row['BusNum']
            ,'BusName': row['BusName']
            ,'NomkV': row['BusNomVolt']
            ,'ID': row['ID']
            ,'Value':row['Vpu']
            ,'Limit':0.0
            ,'Timer': 0.0
            ,'Message': ''
        }

        # Check logic.
        if(row['MvarNom'] == 0):
            # Shunt out of service. Could be switched in-service. 
            if(row['Vpu'] > row['Vmax1']):
                checkResult.update({
                    'Message': 'MSR1 Activation on Vmax1'
                    ,'Limit': row['Vmax1']
                    ,'Timer': row['Tin1']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)
            if(row['Vpu'] > row['Vmax2']):
                checkResult.update({
                    'Message': 'MSR1 Activation on Vmax2'
                    ,'Limit': row['Vmax2']
                    ,'Timer': row['Tin2']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)
        else:
            # Shunt in service. Could be switched out of service.
            if(row['Vpu'] < row['Vmin1']):
                checkResult.update({
                    'Message': 'MSR1 Activation on Vmin1'
                    ,'Limit': row['Vmin1']
                    ,'Timer': row['Tout1']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)
            if(row['Vpu'] < row['Vmin2']):
                checkResult.update({
                    'Message': 'MSR1 Activation on Vmin2'
                    ,'Limit': row['Vmin2']
                    ,'Timer': row['Tout2']
                })
                dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)

    # ------------- Check if LHVRT models will activate. -------------
    dfLhvrtBus = pd.merge(dfLhvrt, dfBus[['BusNum','BusName','BusNomVolt','Vpu']], how='left', on='BusNum')
    dfLhvrtBusGen = pd.merge(dfLhvrtBus, dfGen[['key','Status']], how='left', on='key')

    for index, row in dfLhvrtBusGen.iterrows():
        # Keys for this row
        checkResult = {
            'BusNum': row['BusNum']
            ,'BusName': row['BusName']
            ,'NomkV': row['BusNomVolt']
            ,'ID': row['ID']
            ,'Value': row['Vpu']
            ,'Limit':0.0
            ,'Timer': 0.0
            ,'Message': ''
        }
        # Check logic.
        if(row['Alarm'] == 0 and row['Status_x'] == 'Active' and row['Status_y'] == 'Closed'):
            # Model is set to trip, instead of alarm.
            # Model is Active. 
            # Generator is Closed.

            # See https://www.powerworld.com/WebHelp/Default.htm#TransientModels_HTML/Relay%20Model%20LHVRT.htm
            value = row['Vpu'] - row['Vref']
            for index in range(1,11):
                dvtrp = row['dvtrp'+str(index)]
                dttrp = row['dttrp'+str(index)]
                if((dvtrp > 0) and (value > dvtrp)):
                    checkResult.update({
                        'Message': 'LHVRT Activation on high voltage for dvtrp'+str(index)
                        ,'Limit': dvtrp
                        ,'Timer': dttrp
                    })
                    dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)

                if((dvtrp < 0) and (value < dvtrp)):
                    checkResult.update({
                        'Message': 'LHVRT Activation on low voltage for dvtrp'+str(index)
                        ,'Limit': dvtrp
                        ,'Timer': dttrp
                    })
                    dfCheck = pd.concat([dfCheck, pd.DataFrame([checkResult])], ignore_index=True)

    return dfCheck

if(__name__=='__main__'):
    file_name = r"""C:\TPS\2024-05-21 Check Flat N-0 Stability\17_22HW2a1.pwb"""

    SimAuto = win32com.client.Dispatch("pwrworld.SimulatorAuto")
    chk(SimAuto.OpenCase(file_name), "Opened Case")
    dfCheck = CheckTSLogic()
    dfCheck.to_csv('CheckResult.csv')

    # Example of how to save a case.
    # chk(SimAuto.SaveCase(result_name, 'PWB22', True), "Saved as {}".format(result_name))

    print('done')
