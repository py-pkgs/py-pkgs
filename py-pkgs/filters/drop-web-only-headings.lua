-- PDF only: drop the web landing page's heading (index.qmd). Its content is already
-- hidden from print with a content-visible div; this removes the empty chapter it
-- would otherwise leave behind, so the PDF opens with the preface as in Ed.1.
if not quarto.doc.is_format("latex") then
  return {}
end

return {
  Header = function(el)
    if el.identifier == "welcome-to-python-packages" then
      return {}
    end
  end,
}
