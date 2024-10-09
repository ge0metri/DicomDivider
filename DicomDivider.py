import os, shutil
import pydicom
import wx
import wx.lib.agw.multidirdialog


def run(paths:list, out):
    seriesNumDict = dict()
    kernelDict = dict()
    pixelspacing = dict()
    dicts = [pixelspacing, kernelDict, seriesNumDict]
    tags = [[0x0028, 0x0030], # pixelspacing
            [0x0018, 0x1210], # kernel
            [0x0020, 0x0011]] # seriesnumber
    for path in paths:
            for root, subdirs, files in os.walk(path):
                for file in files:
                    tpath = os.path.join(root, file)
                    data = ()
                    try:
                        data = pydicom.dcmread(tpath, stop_before_pixels=True, specific_tags=tags)
                    except pydicom.errors.InvalidDicomError:
                        print("Tried loading ", tpath, " and failed")
                    if not data:
                        continue
                    for i in range(3):
                        try:
                            key = str(data[tags[i]].value)
                        except Exception as error:
                            key = ["NoPixelSpacing", "NoKernel", "NoSernum"][i]
                        if key in dicts[i]:
                            dicts[i][key] |= set([tpath])
                        else:
                            dicts[i][key] = set([tpath])
    print("Working:")
    for kernelKey, kernelSet in kernelDict.items():
        for pxSpacingKey, pxSpacingSet in pixelspacing.items():
            for serNumKey, serNumSet in seriesNumDict.items():  
                print("|", end="", flush=True)      
                folderSet = kernelSet & pxSpacingSet & serNumSet
                if not folderSet:
                    continue
                newpath = os.path.join(outpath, f"Kernel_{kernelKey}_Px_{pxSpacingKey}")
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                serPath = os.path.join(newpath, f"SerNum_{serNumKey}")
                if not os.path.exists(serPath):
                    os.makedirs(serPath)
                for path in folderSet:
                    shutil.copy(path, serPath)
    print("Done")

if __name__ == '__main__':
    app = wx.App(False)
    app.MainLoop()
    with wx.lib.agw.multidirdialog.MultiDirDialog(None, title = "Choose folder(s) to divide/sort", defaultPath=os.getcwd(),
                         agwStyle=wx.lib.agw.multidirdialog.DD_MULTIPLE|wx.lib.agw.multidirdialog.DD_DIR_MUST_EXIST) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            inpaths = set(dlg.GetPaths())
            print("You selected \n" + '\n'.join(inpaths) + "\nto load\n\n")
        dlg.Destroy()

        dirDialog = wx.DirDialog(None, "Choose main output folder",
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR)
        if dirDialog.ShowModal() == wx.ID_OK:
            outpath = dirDialog.GetPath()
            print('You selected:\n%s\n as save location\n\n' % outpath)
        dirDialog.Destroy()
    run(inpaths, outpath)
    wx.MessageBox("Done")
