# setup a simple gui script to run registration

## IMPLEMETATION DETAILS
# Use PyQt5 to create a simple GUI that allows the user to enter the following:
#   - template file (Label + Textbox + Browse button) - (Row 1) Required
#   - input file (Label + Textbox + Browse button) - (Row 2) Required
#   - output directory (Label + Textbox + Browse button) - (Row 3) Required
#   - checkbox for whether to use rigid, rigid+affine, or rigid+affine+deformable (Row 4) Only one can be selected, default is rigid+affine+deformable
#   - number of threads to use (max is the number of cores on the machine) (Label + Textbox) (Row 5) Default is 1
#   - checkbox to use histogram matching (Row 5) Default is unchecked
#   - checkbox for reproducibility (use the same random seed) (Row 5) Default is checked
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

# create the GUI class
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registration GUI")
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
        self.registration_type_rigid = QtWidgets.QRadioButton("Rigid")
        self.registration_type_rigid.setChecked(False)
        self.registration_type_rigid.toggled.connect(self.set_registration_type)
        self.registration_type_rigid_affine = QtWidgets.QRadioButton("Rigid + Affine")
        self.registration_type_rigid_affine.setChecked(True)
        self.registration_type_rigid_affine.toggled.connect(self.set_registration_type)
        self.registration_type_rigid_affine_deformable = QtWidgets.QRadioButton("Rigid + Affine + Deformable")
        self.registration_type_rigid_affine_deformable.setChecked(False)
        self.registration_type_rigid_affine_deformable.toggled.connect(self.set_registration_type)
        self.registration_type_row.addWidget(self.registration_type_label)
        self.registration_type_row.addWidget(self.registration_type_rigid)
        self.registration_type_row.addWidget(self.registration_type_rigid_affine)
        self.registration_type_row.addWidget(self.registration_type_rigid_affine_deformable)
        self.main_layout.addLayout(self.registration_type_row)

        # create the row 5 layout (histogram matching, reproducibility, number of threads)
        self.num_threads_row = QtWidgets.QHBoxLayout()
        self.num_threads_label = QtWidgets.QLabel("Number of Threads:")
        self.num_threads_textbox = QtWidgets.QLineEdit()
        self.num_threads_textbox.setText("1")
        self.num_threads_textbox.setValidator(QtGui.QIntValidator())
        self.num_threads_textbox.textChanged.connect(self.check_num_threads)
        self.num_threads_row.addWidget(self.num_threads_label)
        self.num_threads_row.addWidget(self.num_threads_textbox)

        self.histogram_matching_checkbox = QtWidgets.QCheckBox("Histogram Matching")
        self.histogram_matching_checkbox.setChecked(False)
        self.num_threads_row.addWidget(self.histogram_matching_checkbox)

        self.reproducibility_checkbox = QtWidgets.QCheckBox("Reproducibility")
        self.reproducibility_checkbox.setChecked(True)
        self.num_threads_row.addWidget(self.reproducibility_checkbox)

        self.main_layout.addLayout(self.num_threads_row)

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
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Template File', os.getcwd(), 'Image Files (*.nii *.nii.gz *.nrrd)')[0]
        # make sure there are no spaces in the filename and alert the user to change it if there are
        if self.verify_no_spaces(filename) is False:
            return
        # set the textbox to the filename
        self.template_textbox.setText(filename)

    # function to browse for the input file
    def browse_input(self):
        # open a file dialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Input File', os.getcwd(), 'Image Files (*.nii *.nii.gz *.nrrd)')[0]
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
        if sender.text() == "Rigid":
            self.registration_type = "rigid"
        elif sender.text() == "Rigid + Affine":
            self.registration_type = "rigid+affine"
        elif sender.text() == "Rigid + Affine + Deformable":
            self.registration_type = "rigid+affine+deformable"

    # function to check the number of threads
    def check_num_threads(self):
        # get the number of threads
        num_threads = self.num_threads_textbox.text()

        # check if the number of threads is a positive integer
        if num_threads.isdigit() and int(num_threads) > 0:
            self.num_threads = num_threads
        else:
            self.num_threads = None

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
        
        # setup output directory
        input_filename = os.path.basename(input_file)
        output_prefix = os.path.splitext(input_filename)[0]+"_registered_"
        output_prefix = os.path.join(output_directory, output_prefix)

        # make sure no files with the same prefix already exist (use glob)
        if len(glob.glob(output_prefix+"*")) > 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Files with the same prefix already exist. Please change the output directory or the input file.")
            return

        # get the number of threads
        num_threads = self.num_threads

        # get the registration type
        registration_type = self.registration_type
        # map it to the correct string
        if registration_type == "rigid":
            registration_type = "r"
        elif registration_type == "rigid+affine":
            registration_type = "a"
        elif registration_type == "rigid+affine+deformable":
            registration_type = "s"

        # get the histogram matching option
        histogram_matching = "1" if self.histogram_matching_checkbox.isChecked() else "0"

        # get the reproducibility option
        reproducibility = "1" if self.reproducibility_checkbox.isChecked() else "0"

        # create the registration command
        registration_command = "antsRegistrationSyNQuick.sh -d 3 -f "+template_file+" -m "+input_file+" -o "+output_prefix+" -n "+num_threads+" -t "+registration_type+" -j "+histogram_matching+" -y "+reproducibility 

        # verify ANTs is installed
        if os.system("antsRegistrationSyNQuick.sh -h") != 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "ANTs is not installed. Please install ANTs and try again.")
            return
        
        # run the registration command in new thread and display the output in the terminal
        self.terminal.append(registration_command)
        self.terminal.append("Running registration...")
        self.terminal.append("")

        # create a new thread to run the registration command
        self.registration_thread = QtCore.QThread()
        self.registration_worker = RegistrationWorker(registration_command)
        self.registration_worker.moveToThread(self.registration_thread)
        self.registration_thread.started.connect(self.registration_worker.run_registration)
        self.registration_worker.finished.connect(self.registration_thread.quit)
        self.registration_worker.finished.connect(self.registration_worker.deleteLater)
        self.registration_thread.finished.connect(self.registration_thread.deleteLater)
        self.registration_worker.progress.connect(self.update_terminal)
        self.registration_thread.start()

    # function to update the terminal
    def update_terminal(self, text):
        self.terminal.append(text)

# create a worker class to run the registration command
class RegistrationWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str)

    def __init__(self, registration_command):
        super().__init__()
        self.registration_command = registration_command

    def run_registration(self):
        # run the registration command
        os.system(self.registration_command)
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



