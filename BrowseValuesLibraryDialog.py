#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This file is part of Beremiz, a Integrated Development Environment for
#programming IEC 61131-3 automates supporting plcopen standard and CanFestival. 
#
#Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD
#
#See COPYING file for copyrights details.
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#General Public License for more details.
#
#You should have received a copy of the GNU General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import wx

[ID_BROWSEVALUESLIBRARYDIALOG, ID_BROWSEVALUESLIBRARYDIALOGSTATICTEXT1,
 ID_BROWSEVALUESLIBRARYDIALOGVALUESLIBRARY
] = [wx.NewId() for _init_ctrls in range(3)]

class BrowseValuesLibraryDialog(wx.Dialog):
    
    if wx.VERSION < (2, 6, 0):
        def Bind(self, event, function, id = None):
            if id is not None:
                event(self, id, function)
            else:
                event(self, function)
    
    def _init_coll_flexGridSizer1_Items(self, parent):
        parent.AddWindow(self.staticText1, 0, border=20, flag=wx.GROW|wx.TOP|wx.LEFT|wx.RIGHT)
        parent.AddWindow(self.ValuesLibrary, 0, border=20, flag=wx.GROW|wx.LEFT|wx.RIGHT)
        parent.AddSizer(self.ButtonSizer, 0, border=20, flag=wx.ALIGN_RIGHT|wx.BOTTOM|wx.LEFT|wx.RIGHT)
    
    def _init_coll_flexGridSizer1_Growables(self, parent):
        parent.AddGrowableCol(0)
        parent.AddGrowableRow(1)
    
    def _init_sizers(self):
        self.flexGridSizer1 = wx.FlexGridSizer(cols=1, hgap=0, rows=3, vgap=10)
        
        self._init_coll_flexGridSizer1_Items(self.flexGridSizer1)
        self._init_coll_flexGridSizer1_Growables(self.flexGridSizer1)
        
        self.SetSizer(self.flexGridSizer1)

    def _init_ctrls(self, prnt, name):
        wx.Dialog.__init__(self, id=ID_BROWSEVALUESLIBRARYDIALOG,
              name='BrowseValueDialog', parent=prnt,
              size=wx.Size(600, 400), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
              title=_('Browse %s library') % name)
        self.SetClientSize(wx.Size(600, 400))

        self.staticText1 = wx.StaticText(id=ID_BROWSEVALUESLIBRARYDIALOGSTATICTEXT1,
              label=_('Choose a %s:') % name, name='staticText1', parent=self,
              pos=wx.Point(0, 0), size=wx.DefaultSize, style=0)
        
        self.ValuesLibrary = wx.TreeCtrl(id=ID_BROWSEVALUESLIBRARYDIALOGVALUESLIBRARY,
              name='ValuesLibrary', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(0, 0), style=wx.TR_HAS_BUTTONS|wx.TR_SINGLE|wx.SUNKEN_BORDER|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT)
        
        self.ButtonSizer = self.CreateButtonSizer(wx.OK|wx.CANCEL|wx.CENTRE)
        if wx.VERSION >= (2, 5, 0):
            self.Bind(wx.EVT_BUTTON, self.OnOK, id=self.ButtonSizer.GetAffirmativeButton().GetId())
        else:
            self.Bind(wx.EVT_BUTTON, self.OnOK, id=self.ButtonSizer.GetChildren()[0].GetSizer().GetChildren()[0].GetWindow().GetId())
        
        self._init_sizers()

    def __init__(self, parent, name, library, default=None):
        self._init_ctrls(parent, name)
        
        root = self.ValuesLibrary.AddRoot("")
        self.GenerateValuesLibraryBranch(root, library, default)

    def GenerateValuesLibraryBranch(self, root, children, default):
        for infos in children:
            item = self.ValuesLibrary.AppendItem(root, infos["name"])
            self.ValuesLibrary.SetPyData(item, infos["infos"])
            if infos["infos"] is not None and infos["infos"] == default:
                self.ValuesLibrary.SelectItem(item)
                self.ValuesLibrary.EnsureVisible(item)
            self.GenerateValuesLibraryBranch(item, infos["children"], default)

    def GetValueInfos(self):
        selected = self.ValuesLibrary.GetSelection()
        return self.ValuesLibrary.GetPyData(selected)

    def OnOK(self, event):
        selected = self.ValuesLibrary.GetSelection()
        if not selected.IsOk() or self.ValuesLibrary.GetPyData(selected) is None:
            message = wx.MessageDialog(self, _("No valid value selected!"), _("Error"), wx.OK|wx.ICON_ERROR)
            message.ShowModal()
            message.Destroy()
        else:
            self.EndModal(wx.ID_OK)
