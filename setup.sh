#!/bin/bash


#Upgrade pip

python.exe -m pip install --upgrade pip


# 3. Pip Install
echo "📦 Installing dependencies..."
pip install -r requirements.txt


# 4. Environment Variables
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your keys!"
else
    echo "✅ .env already exists."
fi

echo "✅ Setup Complete!"
echo "🚀 Run './run.sh' to start the system."

echo 
