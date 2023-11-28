# setup a simple gui script to run warping using ANTs

## START OF CODE
# import the necessary packages
import sys
import os
import glob
from PyQt5 import QtWidgets, QtCore, QtGui

about_message ="""
Welcome to the Kronauer Lab Warping Toolkit!
==========================================================
This program uses ANTs to warp a file using files generated during 
warping.Please make sure that ANTs is installed and the ANTs 
executables are in the PATH environment variable. 
Follow the instructions at our GitHub repository to setup everything:
https://github.com/neurorishika/ant_template_builder

Version: 1.0, November 2023. Developed by Rishika Mohanta.
"""

# create the GUI class
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kronauer Lab Template Warping Kit")
        self.resize(500, 500)
        
        # create the main widget
        self.main_widget = QtWidgets.QWidget()

        # create the layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)


        # create the input file row
        self.input_row = QtWidgets.QHBoxLayout()
        self.input_label = QtWidgets.QLabel("File to Warp:")
        self.input_textbox = QtWidgets.QLineEdit()
        self.input_textbox.setReadOnly(True)
        self.input_browse = QtWidgets.QPushButton("Browse")
        self.input_browse.clicked.connect(self.browse_input)
        self.input_row.addWidget(self.input_label)
        self.input_row.addWidget(self.input_textbox)
        self.input_row.addWidget(self.input_browse)
        self.main_layout.addLayout(self.input_row)

        # create the target reference row
        self.target_row = QtWidgets.QHBoxLayout()
        self.target_label = QtWidgets.QLabel("Target Reference:")
        self.target_textbox = QtWidgets.QLineEdit()
        self.target_textbox.setReadOnly(True)
        self.target_browse = QtWidgets.QPushButton("Browse")
        self.target_browse.clicked.connect(self.browse_target)
        self.target_row.addWidget(self.target_label)
        self.target_row.addWidget(self.target_textbox)
        self.target_row.addWidget(self.target_browse)
        self.main_layout.addLayout(self.target_row)

        # create the output directory row
        self.output_row = QtWidgets.QHBoxLayout()
        self.output_label = QtWidgets.QLabel("Output Directory:")
        self.output_textbox = QtWidgets.QLineEdit()
        self.output_textbox.setReadOnly(True)
        self.output_browse = QtWidgets.QPushButton("Browse")
        self.output_browse.clicked.connect(self.browse_output)
        self.output_row.addWidget(self.output_label)
        self.output_row.addWidget(self.output_textbox)
        self.output_row.addWidget(self.output_browse)
        self.main_layout.addLayout(self.output_row)

        # create the Warp file row
        self.warp_row = QtWidgets.QHBoxLayout()
        self.warp_label = QtWidgets.QLabel("Warp File:")
        self.warp_textbox = QtWidgets.QLineEdit()
        self.warp_textbox.setReadOnly(True)
        self.warp_browse = QtWidgets.QPushButton("Browse")
        self.warp_browse.clicked.connect(self.browse_warp)
        self.warp_row.addWidget(self.warp_label)
        self.warp_row.addWidget(self.warp_textbox)
        self.warp_row.addWidget(self.warp_browse)
        self.main_layout.addLayout(self.warp_row)

        # create the Inverse Warp file row
        self.inverse_warp_row = QtWidgets.QHBoxLayout()
        self.inverse_warp_label = QtWidgets.QLabel("Inverse Warp File:")
        self.inverse_warp_textbox = QtWidgets.QLineEdit()
        self.inverse_warp_textbox.setReadOnly(True)
        self.inverse_warp_browse = QtWidgets.QPushButton("Browse")
        self.inverse_warp_browse.clicked.connect(self.browse_inverse_warp)
        self.inverse_warp_row.addWidget(self.inverse_warp_label)
        self.inverse_warp_row.addWidget(self.inverse_warp_textbox)
        self.inverse_warp_row.addWidget(self.inverse_warp_browse)
        self.main_layout.addLayout(self.inverse_warp_row)

        # create the Affine file row
        self.affine_row = QtWidgets.QHBoxLayout()
        self.affine_label = QtWidgets.QLabel("Affine File:")
        self.affine_textbox = QtWidgets.QLineEdit()
        self.affine_textbox.setReadOnly(True)
        self.affine_browse = QtWidgets.QPushButton("Browse")
        self.affine_browse.clicked.connect(self.browse_affine)
        self.affine_row.addWidget(self.affine_label)
        self.affine_row.addWidget(self.affine_textbox)
        self.affine_row.addWidget(self.affine_browse)
        self.main_layout.addLayout(self.affine_row)

        # create the warping type row
        self.warping_type_row = QtWidgets.QHBoxLayout()
        self.warping_type_label = QtWidgets.QLabel("Warping Type:")
        self.warping_type_to_template = QtWidgets.QRadioButton("To Template")
        self.warping_type_to_template.setChecked(True)
        self.warping_type_to_template.toggled.connect(self.set_warping_type)
        self.warping_type_from_template = QtWidgets.QRadioButton("From Template")
        self.warping_type_from_template.setChecked(False)
        self.warping_type_from_template.toggled.connect(self.set_warping_type)
        self.warping_type = "to_template"
        self.warping_type_row.addWidget(self.warping_type_label)
        self.warping_type_row.addWidget(self.warping_type_to_template)
        self.warping_type_row.addWidget(self.warping_type_from_template)
        self.main_layout.addLayout(self.warping_type_row)

        # create the special warping row (Volume, Segmentation Label, Point Set)
        self.special_warping_row = QtWidgets.QHBoxLayout()
        self.special_warping_label = QtWidgets.QLabel("Type of Data:")
        self.special_warping_volume = QtWidgets.QRadioButton("Volume")
        self.special_warping_volume.setChecked(True)
        self.special_warping_volume.toggled.connect(self.set_special_warping_type)
        self.special_warping_segmentation_label = QtWidgets.QRadioButton("Segmentation Label")
        self.special_warping_segmentation_label.setChecked(False)
        self.special_warping_segmentation_label.toggled.connect(self.set_special_warping_type)
        self.special_warping_point_set = QtWidgets.QRadioButton("Point Set")
        self.special_warping_point_set.setChecked(False)
        self.special_warping_point_set.toggled.connect(self.set_special_warping_type)
        self.special_warping_type = "volume"
        self.special_warping_row.addWidget(self.special_warping_label)
        self.special_warping_row.addWidget(self.special_warping_volume)
        self.special_warping_row.addWidget(self.special_warping_segmentation_label)
        self.special_warping_row.addWidget(self.special_warping_point_set)
        self.main_layout.addLayout(self.special_warping_row)

        # create the row 5 layout (Affine only, Time Series, Low Memory, Mirror before warping)
        self.final_row = QtWidgets.QHBoxLayout()
        self.affine_only_checkbox = QtWidgets.QCheckBox("Affine Only")
        self.affine_only_checkbox.setChecked(False)
        self.time_series_checkbox = QtWidgets.QCheckBox("Time Series")
        self.time_series_checkbox.setChecked(False)
        self.low_memory_checkbox = QtWidgets.QCheckBox("Low Memory")
        self.low_memory_checkbox.setChecked(True)
        self.flip_brain_checkbox = QtWidgets.QCheckBox("Mirror Before Warping")
        self.flip_brain_checkbox.setChecked(False)
        self.final_row.addWidget(self.affine_only_checkbox)
        self.final_row.addWidget(self.time_series_checkbox)
        self.final_row.addWidget(self.low_memory_checkbox)
        self.final_row.addWidget(self.flip_brain_checkbox)
        self.main_layout.addLayout(self.final_row)

        # create the run button
        self.run_button = QtWidgets.QPushButton("Run Warping")
        self.run_button.clicked.connect(self.run_warping)
        self.main_layout.addWidget(self.run_button)

        # create the terminal
        self.terminal = QtWidgets.QTextEdit()
        self.terminal.setReadOnly(True)
        self.main_layout.addWidget(self.terminal)

        # set the main widget
        self.setCentralWidget(self.main_widget)

        # show the window
        self.show()

        # as the program starts, show a message to the user about the program using QtMessageBox
        QtWidgets.QMessageBox.information(self, "About", about_message)

    # function to verify no spaces in the file names or directory names
    def verify_no_spaces(self, filename):
        # check if there are spaces in the filename
        if " " in filename:
            QtWidgets.QMessageBox.warning(self, "Warning", "File name or directory name cannot contain spaces. Please change the file name or directory name.")
            return False
        else:
            return True
        
    # function to browse for the input file (can be Image Files, or csv files)
    def browse_input(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Input File', os.getcwd(), 'Image Files (*.nii.gz *.nrrd) ;; CSV Files (*.csv)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.input_textbox.setText(filename)

    # function to browse for the target reference file
    def browse_target(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Target Reference File', os.getcwd(), 'Image Files (*.nii.gz *.nrrd)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.target_textbox.setText(filename)

    # function to browse for the output directory
    def browse_output(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Output Directory', os.getcwd())
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.output_textbox.setText(filename)

    # function to browse for the warp file
    def browse_warp(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Warp File', os.getcwd(), 'Image Files (*.nii.gz)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.warp_textbox.setText(filename)

    # function to browse for the inverse warp file
    def browse_inverse_warp(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Inverse Warp File', os.getcwd(), 'Image Files (*.nii.gz)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.inverse_warp_textbox.setText(filename)

    # function to browse for the affine file (can be mat files or txt files)
    def browse_affine(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Affine File', os.getcwd(), 'MAT Files (*.mat) ;; TXT Files (*.txt)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.affine_textbox.setText(filename)

    # function to set the warping type
    def set_warping_type(self):
        # get the sender
        sender = self.sender()

        # check which button was clicked
        if sender.text() == "To Template":
            self.warping_type = "to_template"
        elif sender.text() == "From Template":
            self.warping_type = "from_template"
    
    # function to set the special warping type
    def set_special_warping_type(self):
        # get the sender
        sender = self.sender()

        # check which button was clicked
        if sender.text() == "Volume":
            self.special_warping_type = "volume"
        elif sender.text() == "Segmentation Label":
            self.special_warping_type = "segmentation_label"
        elif sender.text() == "Point Set":
            self.special_warping_type = "point_set"


    # function to run the warping using ANTs
    def run_warping(self):
        # get the all files
        input_file = self.input_textbox.text()
        target_file = self.target_textbox.text()
        output_directory = self.output_textbox.text()
        warp_file = self.warp_textbox.text()
        inverse_warp_file = self.inverse_warp_textbox.text()
        affine_file = self.affine_textbox.text()

        # make sure none of the files are empty
        if input_file == "" or target_file == "" or output_directory == "" or warp_file == "" or inverse_warp_file == "" or affine_file == "":
            QtWidgets.QMessageBox.warning(self, "Warning", "All files must be specified.")
            return
        
        # if the output directory does not have a / at the end, add it
        if not output_directory.endswith("/"):
            output_directory += "/"
        
        # setup output directory
        input_filename = os.path.basename(input_file)
        output_prefix = os.path.splitext(input_filename)[0]+"_warped_"
        output_prefix = os.path.join(output_directory, output_prefix)

        # make sure no files with the same prefix already exist (use glob)
        if len(glob.glob(output_prefix+"*")) > 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Files with the same prefix already exist. Please change the output directory or the input file.")
            return

        warping_type = self.warping_type
        special_warping_type = self.special_warping_type
        affine_only = self.affine_only_checkbox.isChecked()
        time_series = self.time_series_checkbox.isChecked()
        low_memory = "1" if self.low_memory_checkbox.isChecked() else "0"
        flip_brain = self.flip_brain_checkbox.isChecked()

        if flip_brain:
            flipped_input_file = output_directory + os.path.splitext(input_filename)[0]+"_flipped"+os.path.splitext(input_filename)[1]
            mirror_file = output_directory + ((input_filename[:-5] if input_filename.endswith(".nrrd") else input_filename[:-7]) + '.mat')
            flip_brain_command1 = "ImageMath 3 {} ReflectionMatrix {} 0 > >(tee -a {}_out.log) 2> >(tee -a {}_err.log >&2)".format(mirror_file, input_file, mirror_file[:-4], mirror_file[:-4])
            flip_brain_command2 = "antsApplyTransforms -d 3 -i {} -o {} -t {} -r {} --float {} > >(tee -a {}_out.log) 2> >(tee -a {}_err.log >&2)".format(input_file, flipped_input_file, mirror_file, input_file, low_memory, flipped_input_file[:-5], flipped_input_file[:-5])
            input_file = flipped_input_file
        else:
            flip_brain_command1 = ""
            flip_brain_command2 = ""


        # create the command
        warping_command = "antsApplyTransforms" # base command
        warping_command += " -d 4 -e 3" if time_series else " -d 3"
        warping_command += " -i "+input_file
        warping_command += " -o "+output_prefix if not special_warping_type == "point_set" else " -o "+output_prefix[:-1]+".csv"
        warping_command += " -r "+target_file

        if warping_type == "to_template":
            if not affine_only:
                warping_command += " -t "+warp_file
            warping_command += " -t "+affine_file
        elif warping_type == "from_template":
            warping_command += " -t ["+affine_file+", 1]"
            if not affine_only:
                warping_command += " -t "+inverse_warp_file

        if special_warping_type == "segmentation_label":
            warping_command += " -n GenericLabel"

        if low_memory:
            warping_command += " --float 1"
        
        # disable all the buttons
        self.run_button.setEnabled(False)
        self.input_browse.setEnabled(False)
        self.target_browse.setEnabled(False)
        self.output_browse.setEnabled(False)
        self.warp_browse.setEnabled(False)
        self.inverse_warp_browse.setEnabled(False)
        self.affine_browse.setEnabled(False)
        self.warping_type_to_template.setEnabled(False)
        self.warping_type_from_template.setEnabled(False)
        self.special_warping_volume.setEnabled(False)
        self.special_warping_segmentation_label.setEnabled(False)
        self.special_warping_point_set.setEnabled(False)
        self.affine_only_checkbox.setEnabled(False)
        self.time_series_checkbox.setEnabled(False)
        self.low_memory_checkbox.setEnabled(False)


        # create a new thread to run the warping command
        self.warping_thread = QtCore.QThread()
        self.warping_worker = WarpingWorker(warping_command, flip_brain_command1, flip_brain_command2)
        self.warping_worker.moveToThread(self.warping_thread)
        self.warping_thread.started.connect(self.warping_worker.run_warping)
        self.warping_worker.finished.connect(self.warping_thread.quit)
        self.warping_worker.finished.connect(self.warping_worker.deleteLater)
        self.warping_thread.finished.connect(self.warping_thread.deleteLater)
        self.warping_worker.progress.connect(self.update_terminal)
        self.warping_thread.start()

        # when the thread is finished, print a message and enable the run button
        self.warping_thread.finished.connect(self.warping_finished)

    # function to print a message when the warping is finished
    def warping_finished(self):
        # enable all the buttons
        self.run_button.setEnabled(True)
        self.input_browse.setEnabled(True)
        self.target_browse.setEnabled(True)
        self.output_browse.setEnabled(True)
        self.warp_browse.setEnabled(True)
        self.inverse_warp_browse.setEnabled(True)
        self.affine_browse.setEnabled(True)
        self.warping_type_to_template.setEnabled(True)
        self.warping_type_from_template.setEnabled(True)
        self.special_warping_volume.setEnabled(True)
        self.special_warping_segmentation_label.setEnabled(True)
        self.special_warping_point_set.setEnabled(True)
        self.affine_only_checkbox.setEnabled(True)
        self.time_series_checkbox.setEnabled(True)
        self.low_memory_checkbox.setEnabled(True)

        # pop up a message box
        QtWidgets.QMessageBox.information(self, "Warping Finished", "Warping finished check the output directory for the registered file: <input_filename>_registered_Warped.nii.gz")

    # function to update the terminal
    def update_terminal(self, text):
        self.terminal.append(text)

# create a worker class to run the warping command
class WarpingWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str)

    def __init__(self, warping_command, flip_brain_command1, flip_brain_command2):
        super().__init__()
        self.warping_command = warping_command
        self.flip_brain_command1 = flip_brain_command1
        self.flip_brain_command2 = flip_brain_command2

    def run_warping(self):
        if self.flip_brain_command1 != "" and self.flip_brain_command2 != "":
            self.progress.emit("Flipping brain...")
            self.progress.emit("")
            # run the flip brain command
            self.progress.emit(self.flip_brain_command1)            
            os.system(self.flip_brain_command1)
            self.progress.emit(self.flip_brain_command2)
            os.system(self.flip_brain_command2)
            self.progress.emit("")
        # run the warping command
        self.progress.emit("Running warping...")
        self.progress.emit("")
        self.progress.emit(self.warping_command)
        os.system(self.warping_command)
        self.progress.emit("")
        self.progress.emit("Warping finished.")
        # emit the finished signal
        self.finished.emit()

# create the main function
def main():
    # create the application
    app = QtWidgets.QApplication(sys.argv)

    # create the main window
    main_window = MainWindow()

    # exit the application
    sys.exit(app.exec_())

# check if the script is being run directly
if __name__ == "__main__":
    main()

## END OF CODE



