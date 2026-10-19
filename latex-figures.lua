-- Keep each source screenshot and its evidence paragraph together.
function Pandoc(doc)
  local blocks = pandoc.List()
  local i = 1
  while i <= #doc.blocks do
    local b = doc.blocks[i]
    if b.t == 'Para' and #b.content == 1 and b.content[1].t == 'Image' then
      local img = b.content[1]
      img.attributes['width'] = '94%'
      img.attributes['height'] = '8.5cm'
      local caption = pandoc.utils.stringify(img.caption)
      img.caption = pandoc.Inlines{}
      blocks:insert(pandoc.RawBlock('latex', '\\par\\addvspace{1em}\\noindent\\begin{minipage}{\\linewidth}\\centering'))
      blocks:insert(b)
      blocks:insert(pandoc.Para{pandoc.Strong{pandoc.Str(caption)}})
      if i < #doc.blocks and pandoc.utils.stringify(doc.blocks[i+1]):match('^画面证据：') then
        blocks:insert(pandoc.RawBlock('latex', '\\raggedright\\footnotesize\\color{muted}'))
        blocks:insert(doc.blocks[i+1])
        i = i + 1
      end
      blocks:insert(pandoc.RawBlock('latex', '\\end{minipage}\\par\\addvspace{1em}'))
    else
      blocks:insert(b)
    end
    i = i + 1
  end
  doc.blocks = blocks
  return doc
end
