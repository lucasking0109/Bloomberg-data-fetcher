#!/bin/bash

# Add remote and push to GitHub
# Replace YOUR_USERNAME with your GitHub username

echo "請輸入您的 GitHub 使用者名稱："
read username

git remote add origin https://github.com/$username/bloomberg-qqq-fetcher.git
git push -u origin main

echo "✅ 推送完成！"
echo "Repository URL: https://github.com/$username/bloomberg-qqq-fetcher"