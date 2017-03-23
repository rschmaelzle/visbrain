"""Main class for settings managment."""
import numpy as np
import os
from PyQt4 import QtGui

from ....utils import transient
from ....utils import listToCsv, listToTxt

__all__ = ['uiScoring']

class uiScoring(object):
    """Enable scoring using the table."""

    def __init__(self):
        """Init."""
        # Fill table on start :
        # self._fcn_Hypno2Score()
        # Add / remove line :
        self._scoreAdd.clicked.connect(self._fcn_addScoreRow)
        self._scoreRm.clicked.connect(self._fcn_rmScoreRow)

        # Table edited :
        self._scoreTable.cellChanged.connect(self._fcn_Score2Hypno)
        
        # Export file :
        self._scoreExport.clicked.connect(self._fcn_exportScore)

    ##########################################################################
    # UPDATE SCORE <=> HYPNO
    ##########################################################################
    def _fcn_Hypno2Score(self):
        """Update hypno table from hypno data."""
        self._hypno = -self._hyp.mesh.pos[:, 1]
        # Avoid updating data while setting cell :
        self._scoreSet = False
        items = ['Wake', 'N1', 'N2', 'N3', 'REM', 'Art']
        # Remove every info in the table :
        self._scoreTable.setRowCount(0)
        # Find unit conversion :
        fact = self._get_factFromUnit()
        # Find transients :
        _, idx, stages = transient(self._hypno, self._time / fact)
        idx = np.round(10. * idx) / 10.
        # Set length of the table :
        self._scoreTable.setRowCount(len(stages))
        # Fill the table :
        for k in range(len(stages)):
            # Add stage start / end :
            self._scoreTable.setItem(k, 0, QtGui.QTableWidgetItem(
                                                              str(idx[k, 0])))
            self._scoreTable.setItem(k, 1, QtGui.QTableWidgetItem(
                                                              str(idx[k, 1])))
            # Add stage :
            self._scoreTable.setItem(k, 2, QtGui.QTableWidgetItem(
                                                          items[stages[k]]))
        self._scoreSet = True

    def _fcn_Score2Hypno(self):
        """Update hypno data from hypno score."""
        if self._scoreSet:
            # Reset hypnogram :
            self._hypno = np.zeros((len(self._time)), dtype=np.float32)
            # Get the current number of rows :
            l = self._scoreTable.rowCount()
            # Reset markers points position and color :
            self._hypedit.pos = np.array([])
            # Loop over table row :
            for k in range(l):
                # Get tstart / tend / stage :
                tstart, tend, stage = self._get_scoreMarker(k)
                # Update pos if not None :
                if tstart is not None:
                    self._hypno[tstart:tend] = stage
            # Update hypnogram :
            self._hypedit._transient(-self._hypno, self._time)
            self._hypedit.color = np.tile(self._hypedit.color_static,
                                          (self._hypedit.pos.shape[0], 1))
            self._hyp.edit.set_data(pos=self._hypedit.pos,
                                    face_color=self._hypedit.color,
                                    size=self._hypedit.size, edge_width=0.)
            self._hyp.set_data(self._sf, self._hypno, self._time)
            self._hyp.edit.update()

    def _get_scoreMarker(self, idx):
        """Get a specific row dat.

        This function insure that the edited line is complete and is properly
        formated.

        Args:
            idx: int
                The row from which get data.

        Returns:
            tstart: float
                Time start (in sample)

            tend: float
                Time end (in sample).

            stage: int
                The stage.
        """
        it = {'art': -1., 'wake': 0., 'n1': 1., 'n2': 2., 'n3': 3., 'rem': 4.}
        # Get unit :
        fact = self._get_factFromUnit()
        # Get selected row :
        # idx = self._scoreTable.currentRow()
        # ============= NON EMPTY ITEM =============
        # Define error message if bad editing :
        errmsg = "\nTable score error. Starting and ending time must be " + \
                 "float numbers (with time start < time end) and stage " + \
                 "must be Wake, N1, N2, N3, REM or Art"
        # Get row data and update if possible:
        tstartItem = self._scoreTable.item(idx, 0)
        tendItem = self._scoreTable.item(idx, 1)
        stageItem = self._scoreTable.item(idx, 2)
        if tstartItem and tendItem and stageItem:
            # ============= PROPER FORMAT =============
            if all([bool(str(tstartItem.text())), bool(str(tendItem.text())),
                   str(stageItem.text()).lower() in it.keys()]):
                try:
                    # Get start / end / stage :
                    tstart = int(float(str(tstartItem.text(
                                                       ))) * fact * self._sf)
                    tend = int(float(str(tendItem.text())) * fact * self._sf)
                    stage = it[str(stageItem.text()).lower()]

                    return tstart, tend, stage
                except:
                    raise ValueError(errmsg)
            else:
                raise ValueError(errmsg)
        else:
            return None, None, None

    ##########################################################################
    # EDITING TABLE
    ##########################################################################
    def _fcn_addScoreRow(self):
        """Add a row to the table."""
        # Increase length :
        self._scoreTable.setRowCount(self._scoreTable.rowCount() + 1)
    
    def _fcn_rmScoreRow(self):
        """Remove selected row."""
        # Remove row :
        self._scoreTable.removeRow(self._scoreTable.currentRow())
        # Update hypnogram from table :
        self._fcn_Score2Hypno()
        
    ##########################################################################
    # EXPORT TABLE
    ##########################################################################
    def _fcn_exportScore(self):
        """Export score info."""
        # Read Table
        rowCount = self._scoreTable.rowCount()
        staInd, endInd, stage = [], [], []
        for row in np.arange(rowCount):
            staInd.append(str(self._scoreTable.item(row, 0).text()))
            endInd.append(str(self._scoreTable.item(row, 1).text()))
            stage.append(str(self._scoreTable.item(row, 2).text()))
        # Find extension :
        selected_ext = str(self._scoreExportAs.currentText())
        # Get file name :
        path = QtGui.QFileDialog.getSaveFileName(
            self, "Save File", "scoring_info",
            filter=selected_ext)
        file = os.path.splitext(str(path))[0]
        if selected_ext.find('csv') + 1:
            listToCsv(file + '.csv', zip(staInd, endInd, stage))
        elif selected_ext.find('txt') + 1:
            listToTxt(file + '.txt', zip(staInd, endInd, stage))
