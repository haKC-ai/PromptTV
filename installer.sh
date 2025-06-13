#!/bin/bash
# Create venv named PromptTV
python3 -m venv PromptTV

# Activate it
source PromptTV/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. To activate your environment later, run:"
echo "source PromptTV/bin/activate"

# Start Streamlit app on 0.0.0.0:2323
echo "Launching Streamlit on port 2323..."
PromptTV/bin/python -m streamlit run app.py --server.address=0.0.0.0 --server.port=2323
