from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import base64
import io
import cmath
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

app = FastAPI()

templates = Jinja2Templates(directory="./templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# example params: a=1%2B1j b=3 c=3
# where %2B is plus sign
@app.get("/solve")
async def solve(a: str, b: str, c: str):
    try:
        a = complex(a)
        b = complex(b)
        c = complex(c)
    except ValueError:
        return {"error": "can't convert params to complex"}

    d = (b ** 2) - 4 * a * c

    sol1 = (-b + cmath.sqrt(d)) / (2 * a)
    sol2 = (-b + cmath.sqrt(d)) / (2 * a)

    return {"roots": [str(sol1).strip("(").strip(")"), str(sol2).strip("(").strip(")")]}


@app.post("/plot")
async def plot(request: Request, a: str = Form(...), b: str = Form(...), c: str = Form(...)):
    try:
        a = complex(a)
        b = complex(b)
        c = complex(c)
    except ValueError:
        return {"error": "can't convert params to complex"}

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    X = W = np.arange(-20.0, 20.0, 0.05)
    X, W = np.meshgrid(X, W)
    complexVals = X + 1j * W

    Y_Z = a * complexVals ** 2 + b * complexVals + c
    Y = Y_Z.real
    Z = Y_Z.imag

    color_dimension = W
    minn, maxx = color_dimension.min(), color_dimension.max()
    norm = matplotlib.colors.Normalize(minn, maxx)
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap='jet')
    m.set_array([])
    fcolors = m.to_rgba(color_dimension)

    ax.plot_surface(X, Y, Z, facecolors=fcolors, vmin=minn, vmax=maxx, shade=False, linewidth=0, antialiased=False)

    ax.set_xlabel('X (Re)')
    ax.set_ylabel('Y (Re)')
    ax.set_zlabel('Z = f(x) (Im)')

    cbr = plt.colorbar(m)
    cbr.ax.set_title('W')

    pngImage = io.BytesIO()
    fig.savefig(pngImage)
    pngImageB64String = base64.b64encode(pngImage.getvalue()).decode('ascii')

    return templates.TemplateResponse("plot.html", {"request": request, "a": a, "b": b, "c": c,
                                                    "picture": pngImageB64String})
