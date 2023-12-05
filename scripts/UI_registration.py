# setup a simple gui script to run registration

## IMPLEMETATION DETAILS
# Use PyQt5 to create a simple GUI that allows the user to enter the following:
#   - template file (Label + Textbox + Browse button) - (Row 1) Required
#   - input file (Label + Textbox + Browse button) - (Row 2) Required
#   - output directory (Label + Textbox + Browse button) - (Row 3) Required
#   - checkbox for whether to use rigid, rigid+affine, or rigid+affine+deformable (Row 4) Only one can be selected, default is rigid+affine+deformable
#   - number of threads to use (max is the number of cores on the machine) (Label + Textbox) (Row 5) Default is 1
#   - checkbox to use histogram matching (Row 5) Default is unchecked
#   - checkbox for quality_check (use the same random seed) (Row 5) Default is checked
#   - checkbox for whether to flip the brain before registration (Row 5) Default is unchecked
#   - button to run the registration (Row 6)
#   - text terminal to display the progress of the registration (Row 7)

# The GUI should be able to handle the following errors:
#   - template file or input file or output directory is not specified
#   - number of threads is not a positive integer
#   - file names or directory names have spaces in them

## START OF CODE
# import the necessary packages
import sys
import os
import glob
from PyQt5 import QtWidgets, QtCore, QtGui

about_message ="""
Welcome to the Kronauer Lab Template Registration Toolkit!
==========================================================
This program uses ANTs to register a brain to a template. 
Please make sure that ANTs is installed and the ANTs executables 
are in the PATH environment variable. 
Follow the instructions at our GitHub repository to setup everything:
https://github.com/neurorishika/ant_template_builder

Version: 1.0, October 2023. Developed by Rishika Mohanta.
"""

# create the GUI class
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kronauer Lab Template Registration Kit")
        self.resize(500, 500)
        
        # create the main widget
        self.main_widget = QtWidgets.QWidget()

        # create the layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        # create the template file row
        self.template_row = QtWidgets.QHBoxLayout()
        self.template_label = QtWidgets.QLabel("Template File:")
        self.template_textbox = QtWidgets.QLineEdit()
        self.template_textbox.setReadOnly(True)
        self.template_browse = QtWidgets.QPushButton("Browse")
        self.template_browse.clicked.connect(self.browse_template)
        self.template_row.addWidget(self.template_label)
        self.template_row.addWidget(self.template_textbox)
        self.template_row.addWidget(self.template_browse)
        self.main_layout.addLayout(self.template_row)

        # create the input file row
        self.input_row = QtWidgets.QHBoxLayout()
        self.input_label = QtWidgets.QLabel("Input File:")
        self.input_textbox = QtWidgets.QLineEdit()
        self.input_textbox.setReadOnly(True)
        self.input_browse = QtWidgets.QPushButton("Browse")
        self.input_browse.clicked.connect(self.browse_input)
        self.input_row.addWidget(self.input_label)
        self.input_row.addWidget(self.input_textbox)
        self.input_row.addWidget(self.input_browse)
        self.main_layout.addLayout(self.input_row)

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

        # create the registration type row 
        self.registration_type_row = QtWidgets.QHBoxLayout()
        self.registration_type_label = QtWidgets.QLabel("Registration Type:")
        self.registration_type_RI = QtWidgets.QRadioButton("Purely Rigid")
        self.registration_type_RI.setChecked(False)
        self.registration_type_RI.toggled.connect(self.set_registration_type)
        self.registration_type_RA = QtWidgets.QRadioButton("Affine + Rigid")
        self.registration_type_RA.setChecked(False)
        self.registration_type_RA.toggled.connect(self.set_registration_type)
        self.registration_type_EL = QtWidgets.QRadioButton("Elastic Registration")
        self.registration_type_EL.setChecked(False)
        self.registration_type_EL.toggled.connect(self.set_registration_type)
        self.registration_type_SY = QtWidgets.QRadioButton("SyN with arbitrary time")
        self.registration_type_SY.setChecked(False)
        self.registration_type_SY.toggled.connect(self.set_registration_type)
        self.registration_type_S2 = QtWidgets.QRadioButton("SyN with 2 time points")
        self.registration_type_S2.setChecked(False)
        self.registration_type_S2.toggled.connect(self.set_registration_type)
        self.registration_type_GR = QtWidgets.QRadioButton("Greedy SyN")
        self.registration_type_GR.setChecked(True) # default registration type
        self.registration_type_GR.toggled.connect(self.set_registration_type)
        self.registration_type_EX = QtWidgets.QRadioButton("Exponential SyN")
        self.registration_type_EX.setChecked(False)
        self.registration_type_EX.toggled.connect(self.set_registration_type)
        self.registration_type_DD = QtWidgets.QRadioButton("Diffeomorphic Demons")
        self.registration_type_DD.setChecked(False)
        self.registration_type_DD.toggled.connect(self.set_registration_type)
        self.registration_type = "GR" # default registration type
        self.registration_type_row.addWidget(self.registration_type_label)
        self.registration_type_row.addWidget(self.registration_type_RI)
        self.registration_type_row.addWidget(self.registration_type_RA)
        self.registration_type_row.addWidget(self.registration_type_EL)
        self.registration_type_row.addWidget(self.registration_type_SY)
        self.registration_type_row.addWidget(self.registration_type_S2)
        self.registration_type_row.addWidget(self.registration_type_GR)
        self.registration_type_row.addWidget(self.registration_type_EX)
        self.registration_type_row.addWidget(self.registration_type_DD)
        self.main_layout.addLayout(self.registration_type_row)

        # create the similarity metric row
        self.similarity_metric_row = QtWidgets.QHBoxLayout()
        self.similarity_metric_label = QtWidgets.QLabel("Similarity Metric:")
        self.similarity_metric_CC = QtWidgets.QRadioButton("Cross Correlation")
        self.similarity_metric_CC.setChecked(True) # default similarity metric
        self.similarity_metric_CC.toggled.connect(self.set_similarity_metric)
        self.similarity_metric_MI = QtWidgets.QRadioButton("Mutual Information")
        self.similarity_metric_MI.setChecked(False)
        self.similarity_metric_MI.toggled.connect(self.set_similarity_metric)
        self.similarity_metric_MSQ = QtWidgets.QRadioButton("Mean Squared Difference")
        self.similarity_metric_MSQ.setChecked(False)
        self.similarity_metric_MSQ.toggled.connect(self.set_similarity_metric)
        self.similarity_metric_PR = QtWidgets.QRadioButton("Probability Mapping")
        self.similarity_metric_PR.setChecked(False)
        self.similarity_metric_PR.toggled.connect(self.set_similarity_metric)
        self.similarity_metric = "CC" # default similarity metric
        self.similarity_metric_row.addWidget(self.similarity_metric_label)
        self.similarity_metric_row.addWidget(self.similarity_metric_CC)
        self.similarity_metric_row.addWidget(self.similarity_metric_MI)
        self.similarity_metric_row.addWidget(self.similarity_metric_MSQ)
        self.similarity_metric_row.addWidget(self.similarity_metric_PR)
        self.main_layout.addLayout(self.similarity_metric_row)



        # create the last row layout (n4 bias field, quality_check, number of threads, flip brain, low memory)
        self.last_row = QtWidgets.QHBoxLayout()
        self.num_iterations_label = QtWidgets.QLabel("Number of Iterations:")
        self.num_iterations_textbox = QtWidgets.QLineEdit()
        self.num_iterations_textbox.setText("30x90x20x8")
        self.num_iterations_textbox.textChanged.connect(self.check_num_iterations)
        self.last_row.addWidget(self.num_iterations_label)
        self.last_row.addWidget(self.num_iterations_textbox)

        self.n4_bias_field_checkbox = QtWidgets.QCheckBox("N4 Bias Field Correction")
        self.n4_bias_field_checkbox.setChecked(True)
        self.last_row.addWidget(self.n4_bias_field_checkbox)

        self.quality_check_checkbox = QtWidgets.QCheckBox("Quality Check")
        self.quality_check_checkbox.setChecked(True)
        self.last_row.addWidget(self.quality_check_checkbox)

        self.low_memory_checkbox = QtWidgets.QCheckBox("Low Memory")
        self.low_memory_checkbox.setChecked(False)
        self.last_row.addWidget(self.low_memory_checkbox)

        self.flip_brain_checkbox = QtWidgets.QCheckBox("Mirror before Registration")
        self.flip_brain_checkbox.setChecked(False)
        self.last_row.addWidget(self.flip_brain_checkbox)

        self.main_layout.addLayout(self.last_row)

        # create the run button
        self.run_button = QtWidgets.QPushButton("Run Registration")
        self.run_button.clicked.connect(self.run_registration)
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

    # function to browse for the template file
    def browse_template(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Template File', os.getcwd(), 'Image Files (*.nii.gz *.nrrd)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.template_textbox.setText(filename)

    # function to browse for the input file
    def browse_input(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Input File', os.getcwd(), 'Image Files (*.nii.gz *.nrrd)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.input_textbox.setText(filename)

    # function to browse for the output directory
    def browse_output(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Output Directory', os.getcwd())
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.output_textbox.setText(filename)

    # function to set the registration type
    def set_registration_type(self):
        # get the sender
        sender = self.sender()

        # check which button was clicked
        if sender.text() == "Purely Rigid":
            self.registration_type = "RI"
        elif sender.text() == "Affine + Rigid":
            self.registration_type = "RA"
        elif sender.text() == "Elastic Registration":
            self.registration_type = "EL"
        elif sender.text() == "SyN with arbitrary time":
            self.registration_type = "SY"
        elif sender.text() == "SyN with 2 time points":
            self.registration_type = "S2"
        elif sender.text() == "Greedy SyN":
            self.registration_type = "GR"
        elif sender.text() == "Exponential SyN":
            self.registration_type = "EX"
        elif sender.text() == "Diffeomorphic Demons":
            self.registration_type = "DD"

    # function to set the similarity metric
    def set_similarity_metric(self):
        # get the sender
        sender = self.sender()

        # check which button was clicked
        if sender.text() == "Cross Correlation":
            self.similarity_metric = "CC"
        elif sender.text() == "Mutual Information":
            self.similarity_metric = "MI"
        elif sender.text() == "Mean Squared Difference":
            self.similarity_metric = "MSQ"
        elif sender.text() == "Probability Mapping":
            self.similarity_metric = "PR"

    # function to check the number of iterations
    def check_num_iterations(self):
        # get the number of iterations
        num_iterations = self.num_iterations_textbox.text()

        # make sure its a series of positive integers separated by x
        try:
            num_iterations = [int(i) for i in num_iterations.split("x")]
            assert all(i > 0 for i in num_iterations)
        except:
            QtWidgets.QMessageBox.warning(self, "Warning", "Number of iterations must be a series of positive integers separated by x.")
            return

    # function to run the registration using ANTs
    def run_registration(self):
        # get the template file
        template_file = self.template_textbox.text()

        # get the input file
        input_file = self.input_textbox.text()

        # get the output directory
        output_directory = self.output_textbox.text()

        # check if the template file, input file, or output directory is not specified
        if template_file == "" or input_file == "" or output_directory == "":
            QtWidgets.QMessageBox.warning(self, "Warning", "Template file, input file, and output directory must be specified.")
            return
        
        # if the output directory does not end with a slash, add a slash
        if not output_directory.endswith("/"):
            output_directory += "/"
        
        # setup output directory
        input_filename = os.path.basename(input_file)
        output_prefix = os.path.splitext(input_filename)[0]+"_registered_"
        output_prefix = os.path.join(output_directory, output_prefix)

        # make sure no files with the same prefix already exist (use glob)
        if len(glob.glob(output_prefix+"*")) > 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Files with the same prefix already exist. Please change the output directory or the input file.")
            return

        # check number of threads
        self.check_num_iterations()

        # get the number of threads
        num_iterations = self.num_iterations

        # get the registration type
        registration_type = self.registration_type

        # get the similarity metric
        similarity_metric = self.similarity_metric

        # get the histogram matching option
        n4_bias_field = "1" if self.n4_bias_field_checkbox.isChecked() else "0"

        # get the quality_check option
        quality_check = "1" if self.quality_check_checkbox.isChecked() else "0"

        # get the flip brain option
        flip_brain = self.flip_brain_checkbox.isChecked()

        # get the low memory option
        low_memory_flip = "1" if self.low_memory_checkbox.isChecked() else "0"

        # create the flip brain command
        if flip_brain:
            # define flipped command
            flipped_input_file = output_directory + os.path.splitext(input_filename)[0]+"_flipped"+os.path.splitext(input_filename)[1]
            mirror_file = output_directory + ((input_filename[:-5] if input_filename.endswith(".nrrd") else input_filename[:-7]) + '.mat')
            flip_brain_command1 = "ImageMath 3 {} ReflectionMatrix {} 0 > >(tee -a {}_out.log) 2> >(tee -a {}_err.log >&2)".format(mirror_file, input_file, mirror_file[:-4], mirror_file[:-4])
            flip_brain_command2 = "antsApplyTransforms -d 3 -i {} -o {} -t {} -r {} --float {} > >(tee -a {}_out.log) 2> >(tee -a {}_err.log >&2)".format(input_file, flipped_input_file, mirror_file, input_file, low_memory_flip, flipped_input_file[:-5], flipped_input_file[:-5])
            input_file = flipped_input_file
        else:
            # define flipped command
            flip_brain_command1 = ""
            flip_brain_command2 = ""
        
        # create the registration command
        registration_command = "antsIntroduction.sh -d 3 -r "+template_file+" -i "+input_file+" -o "+output_prefix+" -m "+num_iterations+" -t "+registration_type+" -n "+n4_bias_field+" -q "+quality_check+" -s "+similarity_metric+" >"+output_prefix+"out.log 2>"+output_prefix+"err.log"

        # disable all the buttons
        self.run_button.setEnabled(False)
        self.template_browse.setEnabled(False)
        self.input_browse.setEnabled(False)
        self.output_browse.setEnabled(False)
        self.registration_type_rigid.setEnabled(False)
        self.registration_type_rigid_affine.setEnabled(False)
        self.registration_type_rigid_affine_deformable.setEnabled(False)
        self.num_iterations_textbox.setEnabled(False)
        self.n4_bias_field_checkbox.setEnabled(False)
        self.quality_check_checkbox.setEnabled(False)
        self.flip_brain_checkbox.setEnabled(False)

        # create a new thread to run the registration command
        self.registration_thread = QtCore.QThread()
        self.registration_worker = RegistrationWorker(registration_command, flip_brain_command1, flip_brain_command2)
        self.registration_worker.moveToThread(self.registration_thread)
        self.registration_thread.started.connect(self.registration_worker.run_registration)
        self.registration_worker.finished.connect(self.registration_thread.quit)
        self.registration_worker.finished.connect(self.registration_worker.deleteLater)
        self.registration_thread.finished.connect(self.registration_thread.deleteLater)
        self.registration_worker.progress.connect(self.update_terminal)
        self.registration_thread.start()

        # when the thread is finished, print a message and enable the run button
        self.registration_thread.finished.connect(self.registration_finished)

    # function to print a message when the registration is finished
    def registration_finished(self):
        # enable all the buttons
        self.run_button.setEnabled(True)
        self.template_browse.setEnabled(True)
        self.input_browse.setEnabled(True)
        self.output_browse.setEnabled(True)
        self.registration_type_rigid.setEnabled(True)
        self.registration_type_rigid_affine.setEnabled(True)
        self.registration_type_rigid_affine_deformable.setEnabled(True)
        self.num_iterations_textbox.setEnabled(True)
        self.n4_bias_field_checkbox.setEnabled(True)
        self.quality_check_checkbox.setEnabled(True)
        self.flip_brain_checkbox.setEnabled(True)

        # pop up a message box
        QtWidgets.QMessageBox.information(self, "Registration Finished", "Registration finished check the output directory for the registered file: <input_filename>_registered_Warped.nii.gz")

    # function to update the terminal
    def update_terminal(self, text):
        self.terminal.append(text)

# create a worker class to run the registration command
class RegistrationWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str)

    def __init__(self, registration_command, flip_brain_command1, flip_brain_command2):
        super().__init__()
        self.registration_command = registration_command
        self.flip_brain_command1 = flip_brain_command1
        self.flip_brain_command2 = flip_brain_command2

    def run_registration(self):
        if self.flip_brain_command1 != "" and self.flip_brain_command2 != "":
            self.progress.emit("Flipping the brain...")
            self.progress.emit("")
            # run the flip brain command
            self.progress.emit(self.flip_brain_command1)
            os.system(self.flip_brain_command1)
            self.progress.emit(self.flip_brain_command2)
            os.system(self.flip_brain_command2)
            self.progress.emit("")
        # run the registration command
        self.progress.emit("Running registration...")
        self.progress.emit("")
        self.progress.emit(self.registration_command)
        os.system(self.registration_command)
        self.progress.emit("")
        self.progress.emit("Registration finished.")
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


