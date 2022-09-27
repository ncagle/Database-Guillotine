import arcpy
import os

class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    self.params[9].filter.list = ['-999999', '12500', '50000', '100000', '250000', '500000']
    self.params[10].category = "Advanced Options"
    self.params[11].category = "Advanced Options"
    self.params[12].category = "Advanced Options"
    self.params[13].category = "Advanced Options"
    self.params[14].category = "Advanced Options"
    self.params[15].category = "Super Secret Parameter"
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parameter
    has been changed."""
    if self.params[0].value == False:
        self.params[1].enabled = 0
        self.params[2].enabled = 0
        self.params[3].enabled = 0
        self.params[4].enabled = 0
        self.params[5].enabled = 0
        self.params[6].enabled = 0
        self.params[7].enabled = 0
        self.params[8].enabled = 0
        self.params[9].enabled = 0
        self.params[10].enabled = 0
        self.params[11].enabled = 0
        self.params[12].enabled = 0
        self.params[13].enabled = 0
        self.params[14].enabled = 0
        self.params[15].enabled = 0
    else:
        self.params[1].enabled = 1
        self.params[2].enabled = 1
        self.params[3].enabled = 1
        if self.params[3].value == True:
            self.params[4].enabled = 1
            self.params[5].enabled = 1
            self.params[6].enabled = 0
        else:
            self.params[4].enabled = 0
            self.params[5].enabled = 0
            self.params[6].enabled = 1

        self.params[7].enabled = 1
        if self.params[7].value == True:
            self.params[8].enabled = 0
        else:
            self.params[8].enabled = 1

        self.params[10].enabled = 1
        if self.params[10].value == True:
            self.params[9].enabled = 0
            self.params[11].enabled = 1
            self.params[12].enabled = 1
        else:
            self.params[9].enabled = 1
            self.params[11].enabled = 0
            self.params[12].enabled = 0

        self.params[13].enabled = 1
        if self.params[13].value == True:
            self.params[14].enabled = 1
        else:
            self.params[14].enabled = 0

    if self.params[4].enabled == 1 and self.params[4].valueAsText is not None:
        if self.params[4].value.endswith('.gdb'):
            self.params[4].value = self.params[4].value[:-len('.gdb')]

    if self.params[4].enabled == 1 and self.params[4].valueAsText is not None:
        if ' ' in self.params[4].valueAsText:
            self.params[4].value = self.params[4].valueAsText.replace(' ', '_')

    if self.params[11].hasError():
        self.params[11].clearMessages()

    if self.params[13].valueAsText == "":
        self.params[13].value = "Ex: HGT >= 46    Applies to all feature classes"

    if self.params[1].hasBeenValidated == False:
        if self.params[1].valueAsText is not None:
            if arcpy.Exists(self.params[1].valueAsText):
                arcpy.env.workspace = self.params[1].valueAsText
                fc_list = arcpy.ListFeatureClasses()
                fc_list.sort()
                self.params[14].filter.list = fc_list
                self.params[14].value = fc_list
                self.params[11].filter.list = fc_list
                if self.params[11].valueAsText is None or self.params[11].valueAsText not in fc_list:
                    self.params[11].value = fc_list[0]
            else:
                self.params[1].setErrorMessage('Input is not a valid TDS dataset')

    if self.params[10].value == True and self.params[1].valueAsText is not None and self.params[11].valueAsText is not None:
        self.params[15].value = os.path.join(self.params[1].valueAsText, self.params[11].valueAsText)

    if self.params[14].valueAsText == ['¯\_(ツ)_/¯']:
        self.params[14].setErrorMessage('Value is required')

    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    self.params[4].clearMessage()
    if self.params[4].enabled == 1:
        if self.params[4].valueAsText is None:
            self.params[4].setErrorMessage('Value is required')
        elif self.params[4].valueAsText == 'Extracted_GDB_Name':
            self.params[4].setErrorMessage('Value is required')
        elif self.params[4].value.endswith('.gdb'):
            self.params[4].setWarningMessage('Please just provide a GDB name without the .gdb extension')

    self.params[5].clearMessage()
    if self.params[5].enabled == 1:
        if self.params[5].valueAsText is None:
            self.params[5].setErrorMessage('Value is required')
        elif len(self.params[5].valueAsText) <= 3:
            self.params[5].setErrorMessage('Value is required')
        elif not "\\" in self.params[5].valueAsText:
            self.params[5].setErrorMessage('Please provide a valid folder path')

    self.params[6].clearMessage()
    if self.params[6].enabled == 1:
        if self.params[6].valueAsText is None:
            self.params[6].setErrorMessage('Value is required')
        elif not self.params[6].valueAsText.endswith('.gdb'):
            self.params[6].setErrorMessage('Please provide a valid geodatabase')

    self.params[8].clearMessage()
    if self.params[8].enabled == 1:
        if self.params[8].valueAsText is None:
            self.params[8].setErrorMessage('Value is required')
        elif len(self.params[8].valueAsText) <= 5:
            self.params[8].setErrorMessage('Value is required')
        elif not "\\" in self.params[8].valueAsText:
            self.params[8].setErrorMessage('Please provide a valid feature class path')

    self.params[9].clearMessage()
    if self.params[9].enabled == 1:
        if self.params[9].valueAsText is None:
            self.params[9].setErrorMessage('Value is required')

    self.params[12].clearMessage()
    if self.params[12].enabled == 1:
        if self.params[12].valueAsText is None:
            self.params[12].setErrorMessage('Value is required')
        if "Ex:" in self.params[12].valueAsText:
            self.params[12].setErrorMessage('Value is required')

    self.params[15].clearMessage()

    return
