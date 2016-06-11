"""
RetimeCamera v1.2
Copyright 2015 Mark Justison
Last Revision: 31, May 2016
"""

# ################################################################
# Add to menu.py: ################################################
# import RetimeCamera ############################################
# m.addCommand('Retime Camera', 'RetimeCamera.create_RCPanel()') #
# ################################################################

import nuke
import nukescripts

class RetimeCamera(nukescripts.PythonPanel):
    """
    Select a Camera and a retime node (either oflow or kronos).
    retimeCamera will created a new camera with updated animation
    based on the retime selected.
    """

    def __init__(self, cameraNode, retimeNode):
        nukescripts.PythonPanel.__init__(self, 'RetimeCamera', 'org.magpie.retimecamera')
        # INSTANCE VARIABLES
        global FIRST_FRAME
        global LAST_FRAME
        FIRST_FRAME = nuke.root().firstFrame()
        LAST_FRAME = nuke.root().lastFrame()
        # NODE-SPECIFIC INSTANCE VARIABLES
        self.cameraNode = cameraNode
        self.cameraNode_Name = cameraNode.name()
        self.retimeNode = retimeNode
        self.retimeNode_Name = retimeNode.name()

        # RETIME METHOD VARIABLE ASSIGNMENT
        # Depending on type of retime (legacy OFlow vs N9 OFlow and Kronos), these must change
        if self.retimeNode.Class() == 'OFXuk.co.thefoundry.time.oflow_v100':
            self.retime_OutputSpeed = 'curve(' + self.retimeNode_Name + '.timingSpeed)'
            self.retime_Frame = 'curve(' + self.retimeNode_Name + '.timingFrame)'
            # pulldown selection box
            self.timingMethodPulldown = nuke.Enumeration_Knob('', '', ['Speed', 'Source Frame'])
        else:
            self.retime_OutputSpeed = 'curve(' + self.retimeNode_Name + '.timingOutputSpeed)'
            self.retime_InputSpeed = 'curve(' + self.retimeNode_Name + '.timingInputSpeed)'
            self.retime_Frame = 'curve(' + self.retimeNode_Name + '.timingFrame2)'
            # pulldown selection box
            self.timingMethodPulldown = nuke.Enumeration_Knob('', '', ['Output Speed', 'Input Speed', 'Frame'])

        # CREATE KNOBS

        # DIVIDERS
        self.div1 = nuke.Text_Knob('div1', '', '')
        self.div2 = nuke.Text_Knob('div2', '', '')

        # TEXT
        self.toolName = nuke.Text_Knob('', '', 'Retime Camera v1.1')
        self.description = nuke.Text_Knob('', '', 'Creates a new retimed camera from ' +
                                          self.retimeNode_Name + ' and ' +
                                          self.cameraNode_Name + ' nodes.')
        self.pulldownText = nuke.Text_Knob('', '', 'Select timing method - ')

        # PULLDOWN SELECTION BOX
        # keep pull-downs on same line
        self.pulldownText.clearFlag(nuke.STARTLINE)
        self.timingMethodPulldown.clearFlag(nuke.STARTLINE)

        # add button #
        self.execute = nuke.PyScript_Knob('', 'Create Retimed Camera', '')

        # populate knob list #
        self.knobSet = [self.toolName, self.description, self.div1,
                        self.pulldownText, self.timingMethodPulldown, self.div2, self.execute]

        # add knobs #
        for knob in range(len(self.knobSet)):
            self.addKnob(self.knobSet[knob])

        # add cancel button #
        if self.cancelButton is None:
            self.cancelButton = nuke.Script_Knob('Cancel')
            self.addKnob(self.cancelButton)
    # end __INIT__

    def create_retimedCameraNode(self):
        self.cameraNode['selected'].setValue(True)
        self.retimeNode['selected'].setValue(False)

        cameraCopy = self.copyNode()
        cameraCopy['name'].setValue(self.rename_copiedNodeVersion(self.cameraNode))
        timingMethod_String = self.timingMethodString(self.timingMethodPulldown.value())

        if (timingMethod_String is not 'timingFrame') and (timingMethod_String is not 'timingFrame2'):
            (self.retimeNode, timingMethod_String) = self.convert_retimeToFrame(self.retimeNode, timingMethod_String)
            self.retimeNode_Name = self.retimeNode.name()

        cameraCopy["rotate"].setExpression("curve(" + self.retimeNode_Name + "." + timingMethod_String + ")")

        if cameraCopy["translate"].isAnimated():
            cameraCopy["translate"].setExpression("curve(" + self.retimeNode_Name + "." + timingMethod_String + ")")

        # verify
        nuke.message(cameraCopy['name'].getValue() + " created. Retimed from " +
                     self.retimeNode['name'].getValue() + ".")
    # end create_retimedCameraNode()

    def timingMethodString(self, methodType):
        """
            Takes knob variable and returns
            related expression string.
        """
        timingMethodString = None
        if methodType == 'Frame':
            timingMethodString = 'timingFrame2'
        elif methodType == 'Source Frame':
            timingMethodString = 'timingFrame'
        elif methodType == 'Output Speed':
            timingMethodString = 'timingOutputSpeed'
        elif methodType == 'Input Speed':
            timingMethodString = 'timingInputSpeed'
        elif methodType == 'Speed':
            timingMethodString = 'timingSpeed'
        return timingMethodString
    # end timingMethodString()

    def convert_retimeToFrame(self, retimeNode, TM_String):
        """
            takes retime node and method of retime used.
            converts speed data to frame data and returns copy
            of retime node with data set to the frame method
        """
        for node in nuke.allNodes():
            node['selected'].setValue(False)
        retimeNode['selected'].setValue(True)
        rtNodeCopy = self.copyNode()
        rtNodeCopy['name'].setValue(self.rename_copiedNodeVersion(retimeNode))

        if retimeNode.Class() != 'OFlow2' and retimeNode.Class() != 'Kronos':
            rtNodeCopy['timing'].setValue(1)
            rtNodeCopy['timingFrame'].setAnimated()
            for frame in range(LAST_FRAME + 1):
                rtNodeCopy['timingFrame'].setValueAt((
                    (frame - FIRST_FRAME) * retimeNode[TM_String].getValueAt(frame) + FIRST_FRAME), frame)
            TM_String = 'timingFrame'
        else:
            rtNodeCopy['timing2'].setValue(2)
            rtNodeCopy['timingFrame2'].setAnimated()
            for frame in range(LAST_FRAME + 1):
                rtNodeCopy['timingFrame2'].setValueAt((
                    (frame - FIRST_FRAME) * retimeNode[TM_String].getValueAt(frame) + FIRST_FRAME), frame)
            TM_String = 'timingFrame2'
        return (rtNodeCopy, TM_String)
    # end convert_retimeToFrame()

    ########################
    # copies selected node #
    ########################
    # needs exception for no nodes selected
    def copyNode(self):
        nuke.nodeCopy('%clipboard%')
        copied = nuke.nodePaste('%clipboard%')
        copied.setInput(0, None)
        # remove dependencies
        if len(copied.dependent()) > 0:
            copied.dependent()[0].setInput(0, None)
        return copied
    # end copyNode()

    def rename_copiedNodeVersion(self, node_namedFrom):
        name_forNode = None
        for node in nuke.allNodes():
            if node['name'].getValue().find(node_namedFrom['name'].getValue() + "_copy_") != -1:
                print("found name match") # tests
                vers_num = int(node['name'].getValue().split("_copy_")[1]) + 1
                print(vers_num) # tests
                name_forNode = node_namedFrom['name'].getValue() + '_copy_' + str(vers_num)
                print(name_forNode) # tests
                return name_forNode
            else:
                name_forNode = node_namedFrom['name'].getValue() + '_copy_1'
        return name_forNode
    # end rename_copiedNodeVersion()

    #####################################
    # check to see if a knob is changed #
    #####################################
    def knobChanged(self, knob):
        if knob is self.execute:
            self.create_retimedCameraNode()
            # close panel
            self.finishModalDialog(True)
    # end knobChanged()

####################################
# Create RetimeCamera Dialog Panel #
####################################
def create_RCPanel():
    try:
        nodes = nuke.selectedNodes()
        areNodes = 0
        camNode = None
        retimeNode = None

        for node in nodes:
            if (node.Class() == 'Axis2') or (node.Class() == 'Axis') or (node.Class() == 'Camera') or (node.Class() == 'Camera2'):
                camNode = node
                areNodes += 1
            elif (node.Class() == 'Kronos') or (node.Class() == 'OFlow2') or (node.Class() == 'OFXuk.co.thefoundry.time.oflow_v100'):
                retimeNode = node
                areNodes += 1

        if areNodes != 2:
            nuke.message("please select your camera(or animated axis) and retime nodes")
            return
        else:
            return RetimeCamera(camNode, retimeNode).showModal()
    except ValueError:
        nuke.message("please select your camera(or animated axis) and retime nodes")
# end create_RCPanel()
