#!/bin/bash

# Deployment script for XX-Commerce to school server
# Usage: ./deploy_to_school_server.sh

echo "🚀 Deploying XX-Commerce to school server..."

# School server details
SCHOOL_SERVER="student_user18@172.16.6.100"
SCHOOL_PATH="/home/student_user18/XX-Commerce"

# Files to deploy
FILES=(
    "templates/store/category_list.html"
    "store/cart_views.py"
    "store/models.py"
    "store/management/commands/cleanup_duplicate_carts.py"
    "xxcommerce/urls.py"
    "store/admin.py"
    "store/apps.py"
)

echo "📁 Copying files to school server..."

# Copy each file
for file in "${FILES[@]}"; do
    echo "Copying $file..."
    scp "$file" "$SCHOOL_SERVER:$SCHOOL_PATH/$file"
    if [ $? -eq 0 ]; then
        echo "✅ $file copied successfully"
    else
        echo "❌ Failed to copy $file"
    fi
done

echo "🔧 Running commands on school server..."

# Run commands on school server
ssh "$SCHOOL_SERVER" << 'EOF'
cd /home/student_user18/XX-Commerce

echo "Running migrations..."
python3 manage.py migrate

echo "Cleaning up duplicate carts..."
python3 manage.py cleanup_duplicate_carts

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "✅ Deployment completed!"
echo "You can now restart your server with:"
echo "python3 manage.py runserver 0.0.0.0:50018"
EOF

echo "🎉 Deployment script completed!"
