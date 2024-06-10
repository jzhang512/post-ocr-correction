// Set DYLD_LIBRARY_PATH to include the path to libcairo.2.dylib
process.env.DYLD_LIBRARY_PATH = '/opt/homebrew/lib:' + (process.env.DYLD_LIBRARY_PATH || '');

const fs = require('fs');
const path = require('path');
const { createWorker } = require('tesseract.js');
const pdfConvert = require('pdf-poppler'); // Ensure you have installed pdf-poppler

async function convertPDFtoImage(pdfPath, outputPath) {
  let opts = {
    format: 'jpeg',
    out_dir: outputPath,
    out_prefix: path.basename(pdfPath, path.extname(pdfPath)),
    page: null // Convert all pages
  };

  return pdfConvert.convert(pdfPath, opts);
}

// --------------------------------------------------------------------

// Main. Assumes files are not in pdf format!
async function recognizeTextFromFiles(folderPath) {
  const worker = await createWorker();

  try {
    const files = fs.readdirSync(folderPath);
    for (const file of files) {
      console.assert(!file.toLowerCase().endsWith('.pdf'));
      const filePath = path.join(folderPath, file);

      try {
        const { data: { text } } = await worker.recognize(filePath);
        console.log("$%$%$%$%*#DELZ" + file)    // $%$%$%$%*#DELZ will be our delimiter. See re_OCR() in qe_step.py.
        console.log(text);
      } catch (error) {
        console.error(`Error recognizing text from ${filePath}:`, error);
      }
    }
  } catch (error) {
    console.error('Error reading folder:', error);
  } finally {
    await worker.terminate();
  }
}

// --------------------------------------------------------------------

// Should be the path to folder where all images are to be re-OCR'ed.
const args = process.argv.slice(2)

if (args.length > 0) {
    recognizeTextFromFiles(args[0])
}
else {
    console.log("No folder path provided.")
}

