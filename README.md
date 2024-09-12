Warning: This is an unfinished project I'm now repurposing.

Old code can be seen under the `src` directory on the `main` branch.

## 1. Installation:
To install, run `pip install -r requirements.txt`

## 2. Command Builder
The `pdf_command_builder` takes in a pdf manual input, parses the commands, and returns a json file containing command details.
  - Due to some text formatting issues inside the pdf I used, the raw strings contain randomly placed special characters such as `\n`, so there's extra formatting commands called as a result.
  - It is able to process 350+ of the 500 available commands inside the PDF. Each command output contains a property `is_implemented` to determine if it was processed by the code snippet or not.
  - Environment variables are listed below (can also be passed in as command line inputs):


Variable Name | Description | Example 
   --- | --- | --- 
   `PDF_FILE_PATH`| Path to the PDF to be processed | `../example_pdf.pdf` 
   `OUTPUT_FILE_PATH`| Output File Path | `output.json`

## 3. UI code
This is written in Kivy. It's unfinished, and I'm not finishing it in Kivy: I'm swapping frameworks for it.

If you really want to see it in action, after executing the installation step, run `python src/main_gui.py`. Currently, it provides a UI that allows users to filter out and scroll through created commands.