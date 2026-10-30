"""Assemble ol.html from ol_src.html + shared parts of templates/uc-sehv-tap/sehv.html."""
import os
D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, '..', 'uc-sehv-tap', 'sehv.html')).read()
cut = lambda a, b: src[src.index(a):src.index(b)]
css_base = cut('<style>', '/* phone */')[7:]
css_s67 = cut('/* S6/S7 */', '</style>')
helpers = cut('<script>', '// ---------------- site ----------------')[8:]
s6 = cut("  if(show('s6'", "window.render=render").rstrip()[:-1]
html_s67 = cut('<div class="full" id="s6">', '<div class="full" id="flashL">')
html_s67 = html_s67.replace('id="l6a">Səhvi<', 'id="l6a">Qoy saytın<').replace('biz tapaq.', 'cavab versin.')
grain = cut("const gctx", "const SH2")
out = open(os.path.join(D, 'ol_src.html')).read()
for k, v in dict(CSS_BASE=css_base, CSS_S67=css_s67, HELPERS=helpers, S6=s6, HTML_S67=html_s67, GRAIN=grain).items():
    out = out.replace('{{%s}}' % k, v)
open(os.path.join(D, 'ol.html'), 'w').write(out)
print('ok', len(out))
