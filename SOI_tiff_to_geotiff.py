# gdal must match system gdal
# gdainfo --version
# pip install gdal==2.4
import gdal
import osr
import pickle
import numpy
import csv
import shutil
import os
import pandas as pd

from tkinter import *
from tkinter.filedialog import askopenfilename
# pip install pillow
from PIL import Image, ImageTk, ImageDraw
os.mkdir('./SOI_tiffs_gcps/')

# Extract the map area
def extractMap(path):
    event2canvas = lambda e, c: (c.canvasx(e.x), c.canvasy(e.y))
    if __name__ == "__main__":
        root = Tk()

        #setting up a tkinter canvas with scrollbars
        frame = Frame(root, width=1500, height=1000, bd=2, relief=SUNKEN)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        xscroll = Scrollbar(frame, orient=HORIZONTAL)
        xscroll.grid(row=1, column=0, sticky=E+W)
        yscroll = Scrollbar(frame)
        yscroll.grid(row=0, column=1, sticky=N+S)
        canvas = Canvas(frame, bd=0, width=1500, height=1000, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        canvas.grid(row=0, column=0, sticky=N+S+E+W)
        xscroll.config(command=canvas.xview)
        yscroll.config(command=canvas.yview)
        frame.pack(fill=BOTH,expand=True)

        #adding the image
        # File = askopenfilename(parent=root, initialdir="./",title='Choose an image.')
        # print("opening %s" % File)
        img = ImageTk.PhotoImage(Image.open('./SOI_tiffs/' + path))
        canvas.create_image(0,0,image=img,anchor="nw")
        canvas.config(scrollregion=canvas.bbox(ALL))

        global corners_pixels
        corners_pixels = []
        #function to be called when mouse is clicked
        def printcoords(event):
            #outputting x and y coords to console
            cx, cy = event2canvas(event, canvas)
            print ("(%d, %d) / (%d, %d)" % (event.x,event.y,cx,cy))
            if [cx,cy] not in corners_pixels:
                print(len(corners_pixels))
                corners_pixels.append([cx,cy])
                if len(corners_pixels) > 3:
                    root.destroy()

    #mouseclick event
    canvas.bind("<ButtonPress-1>",printcoords)
    # canvas.bind("<ButtonRelease-1>",printcoords)
    root.mainloop()

def createCornerLatLng(sheet_r):
    df = pd.read_csv('./SOI_grid.csv', index_col='sheet_ref')
    row = df.loc[sheet_r]
    x_west_edge = row['west']
    y_south_edge = row['south']
    print(x_west_edge)

    corners_latLng = {
      'x_west_edge': x_west_edge,
      # 'x_west_grat' : x_west_edge + 0.08333,
      # 'x_east_grat': x_west_edge + 0.1667,
      'x_east_edge': x_west_edge + 0.25,
      'y_south_edge': y_south_edge,
      # 'y_south_grat': y_south_edge + 0.08333,
      # 'y_north_grat' : y_south_edge + 0.1667,
      'y_north_edge': y_south_edge + 0.25
    }

    # TODO Sort corners_pixels
    corners = [
      {'location': [corners_latLng['x_west_edge'], corners_latLng['y_north_edge']], 'pixel': corners_pixels[0]},
      {'location': [corners_latLng['x_east_edge'], corners_latLng['y_north_edge']], 'pixel': corners_pixels[1]},
      {'location': [corners_latLng['x_east_edge'], corners_latLng['y_south_edge']], 'pixel': corners_pixels[2]},
      {'location': [corners_latLng['x_west_edge'], corners_latLng['y_south_edge']], 'pixel': corners_pixels[3]}
    ]
    # TODO Save corners in csv

    print(corners)
    return corners

def createGcps(coords):
    gcps = []
    for coord in coords:
        # 'coord' = {'location': [-3.756732387660781, 50.57983418053561], 'pixel': [2164, 966]}
        col = coord['pixel'][0]
        row = coord['pixel'][1]
        x = coord['location'][0]
        y = coord['location'][1]
        z = 0
        gcp = gdal.GCP(x, y, z, col, row)
        gcps.append(gcp)
    return gcps

# # https://stackoverflow.com/questions/55681995/how-to-georeference-an-unreferenced-aerial-imgage-using-ground-control-points-in
def addGcps(path, gcps):
  # os.mkdir('./SOI_tiffs_cut/')
  # src = './SOI_tiffs_cut/' + path
  src = './SOI_tiffs/' + path
  dst = './SOI_tiffs_gcps/' + path
  # Create a copy of the original file and save it as the output filename:
  shutil.copy(src, dst)
  # Open the output file for writing for writing:
  ds = gdal.Open(dst, gdal.GA_Update)
  # Set spatial reference:
  sr = osr.SpatialReference()
  sr.ImportFromEPSG(4326)

  # Apply the GCPs to the open output file:
  ds.SetGCPs(gcps, sr.ExportToWkt())

  # Close the output file in order to be able to work with it in other programs:
  ds = None

def createGeoTiff(path):
  src = './SOI_tiffs_gcps/' + path
  dst = './SOI_geotiffs/' + path
  input_raster = gdal.Open(src)
  gdal.Warp(dst,input_raster,dstSRS='EPSG:4326',dstNodata=255)

tiffpaths = os.listdir('./SOI_tiffs')

for path in tiffpaths:
    print(path)
    sheet_ref = path.split('.')[0]
    extractMap(path)
    corners = createCornerLatLng(sheet_ref)
    gcps = createGcps(corners)
    addGcps(path, gcps)
    createGeoTiff(path)

shutil.rmtree('./SOI_tiffs_gcps/')
