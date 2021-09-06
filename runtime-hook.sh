# script to clean up index.html and prettify the resultant url
# by default jupyter-book just publishes index.html with a redirect
# to welcome.html. This is bad because the resultant url always
# looks like py-pkgs.org/welcome, but I want it to just be
# py-pkgs.org. So I'm copying the content of welcome.html and then
# modifying the ToC reference to welcome.html
cp py-pkgs/_build/html/welcome.html py-pkgs/_build/html/index.html
if [ "$(uname)" == "Darwin" ]; then
    sed -i '' 's/href="#"/href="welcome.html"/g' py-pkgs/_build/html/index.html
    sed -i '' 's/py-pkgs.org\/welcome.html/py-pkgs.org/g' py-pkgs/_build/html/index.html
    perl -i -pe 's/\\index\{.*?\}//g' ./_build/html/*.html  # remove \index{*} made for PDF-render
    echo runtime-hook successfully ran in OS $(uname)!
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    sed -i 's/href="#"/href="welcome.html"/g' py-pkgs/_build/html/index.html
    sed -i 's/py-pkgs.org\/welcome.html/py-pkgs.org/g' py-pkgs/_build/html/index.html
    find ./_build/html/*.html -type f -exec sed -i -e 's/\\index\{.*?\}//g' {} \;  # remove \index{*} made for PDF-render
    echo runtime-hook successfully ran in OS $(uname)!
else
    echo runtime-hook not run.
fi