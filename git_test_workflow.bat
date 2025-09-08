# Git workflow for testing simplified manifest

# 1. Create feature branch for testing
git checkout -b test-connect-button-fix

# 2. Backup current DCR implementation
copy api\index.py api\index_dcr_version.py

# 3. Replace with simplified test version
copy api\index_test_connect_button.py api\index.py

# 4. Commit the test version
git add .
git commit -m "Test: Remove oauth:true and configure endpoint to trigger Connect button

External AI analysis suggests Claude shows Configure when manifest declares:
- oauth: true 
- configure endpoint

This test removes both to see if Connect button appears instead.

Based on findings from ChatGPT analysis of Claude UI state machine."

# 5. Push and deploy
git push origin test-connect-button-fix
vercel --prod

# 6. Test in Claude Desktop:
# - Remove existing connector  
# - Add: https://google-workspace-remote-vercel.vercel.app
# - Check if shows Connect instead of Configure

echo "Ready to test simplified manifest approach"
