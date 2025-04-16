# Configurational LLM

A cross-platform application for processing scientific literature using large language models, with support for customised APIs.

Software:
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15200045.svg)](https://doi.org/10.5281/zenodo.15200045)

Related paper of testing validity and reliability:
<a href="https://doi.org/10.31235/osf.io/quxga_v1"><img src="https://zenodo.org/badge/DOI/10.31235/osf.io/quxga_v1.svg" alt="DOI"></a>


## Overview

Configurational LLM enables researchers to systematically process scientific papers and research documents through LLMs. The application:

- Calls Claude API or OpenAI compatible API with reasoning capabilities
- Processes one file at a time, with context reset between files
- Uses customizable prompts and messages
- Records LLM outputs and merges them into a comprehensive document
- Creates separate logs for prompts and messages

## Features

- **API Settings**: Configure API settings for Claude or OpenAI
- **Prompts Editor**: Customize system prompts
- **Message Editor**: Configure user messages
- **Files Library**: Manage files for processing
- **Live Output**: View real-time LLM responses and extracted tables

## Requirements

- Python 3.8 or higher
- PySide6 (Qt for Python)
- Internet connection
- Claude API key, Gemini API key, OpenAI API key, or other third party API key

## Installation

### From GitHub

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/configurational-llm.git
   cd configurational-llm
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Project Structure

```
configurational-llm/
├── core/                 # Core functionality
│   └── llm_processor.py  # LLM processing logic
├── gui/                  # GUI components
│   ├── pages/            # Application pages
│   ├── main_window.py    # Main application window
│   └── styles.py         # UI styling
├── utils/                # Utility functions
├── logos/                # Application logos
├── resources/            # Additional resources
│   └── translations/     # Localization files
├── main.py               # Application entry point
└── requirements.txt      # Dependencies
```

## Getting Started

1. Launch the application
2. Go to API Settings and enter your API key (Gemini, Claude, OpenAI, or other third party APIs)
3. Customize prompts and messages as needed
4. Add files to the Files Library
5. Click "Process All Files" to start the analysis
6. View results in the Live Output tab

## File Types

The application supports various file types including:
- PDFs
- Text file
- CSV files
- Markdown files
- JSON files
- HTML files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contributors

CRediT statement:
Yuming (Trayten) Zhang: Conceptualisation, Methodology, Software, Validation, Resources, Visualisation. 
Linrui Zhong: Validation, Investigation. 
Tiago Moreira: Supervision (external to the core team). 
Jonathan Wistow: Supervision (external to the core team).

## Cite this software

APA:
Zhang, Y., Zhong, L., Moreira, T., & Wistow, J. (2025). Configurational-LLM: A Configurable Document Processing Application using Large Language Models. Zenodo. https://doi.org/10.5281/zenodo.15200045

Bibtex:
@misc{zhang2025configurational,
  author = {Zhang, Y. and Zhong, L. and Moreira, T. and Wistow, J.},
  title = {Configurational-LLM: A Configurable Document Processing Application using Large Language Models},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.15200045},
  url = {https://doi.org/10.5281/zenodo.15200045}
}


## License

Guidance and Processing core: © 2025 configurational.tech contributors. Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0).

This work is licensed under a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](http://creativecommons.org/licenses/by-nc-nd/4.0/).

Software design: © 2025 Trayten Yuming Zhang - Non-commercial use only.

