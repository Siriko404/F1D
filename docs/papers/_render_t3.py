import pymupdf
doc = pymupdf.open("campello_etal_2022_brexit_jfqa.pdf")
pg = doc[22]
# render the coefficient region at high DPI for ground-truth viewing
mat = pymupdf.Matrix(300/72, 300/72)
pix = pg.get_pixmap(matrix=mat)
pix.save("_t3_full.png")
print("page rect:", pg.rect)
print("saved _t3_full.png", pix.width, "x", pix.height)
