sudo docker-compose down -v

cd ..

sudo rm -rf AnkyloScan

# Installation of tool
sudo apt update -y && sudo apt install -y docker.io docker-compose

# Installation of AnkyloScan
git clone https://github.com/DotAdrien/AnkyloScan/tree/Version-1
cd AnkyloScan

# Generate unique password (une seule fois) 🔑
echo "ADMIN_PASSWORD=$(openssl rand -base64 32)" > .env

# Start 🚀
sudo docker-compose up --build
