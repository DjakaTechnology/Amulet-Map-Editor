import wx
import wx.lib.scrolledpanel
from typing import Tuple, Optional

import PyMCTranslate
from amulet.api.block import PropertyType, Block
from amulet.api.block_entity import BlockEntity

from amulet_map_editor.api.wx.ui.base_define import BaseDefine
from amulet_map_editor.api.wx.ui.block_select import BlockSelect

from amulet_map_editor.api.wx.ui.block_select.properties import (
    PropertySelect,
    WildcardPropertySelect,
    EVT_PROPERTIES_CHANGE,
)


class BlockDefine(BaseDefine):
    """
    A UI that merges a version select widget with a block select widget and a property select.
    """

    def __init__(
        self,
        parent,
        translation_manager: PyMCTranslate.TranslationManager,
        orientation=wx.VERTICAL,
        platform: str = None,
        version_number: Tuple[int, int, int] = None,
        force_blockstate: bool = None,
        namespace: str = None,
        block_name: str = None,
        properties: PropertyType = None,
        wildcard_properties=False,
        show_pick_block: bool = False,
        **kwargs,
    ):
        super().__init__(
            parent,
            translation_manager,
            BlockSelect,
            orientation,
            platform,
            version_number,
            namespace,
            default_name=block_name,
            show_pick=show_pick_block,
            force_blockstate=force_blockstate,
            **kwargs,
        )

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        border = wx.LEFT if orientation == wx.HORIZONTAL else wx.TOP
        self._sizer.Add(right_sizer, 1, wx.EXPAND | border, 5)
        self._wildcard_mode = wildcard_properties
        if wildcard_properties:
            self._property_picker = PropertySelect(
                self,
                translation_manager,
                self._version_picker.platform,
                self._version_picker.version_number,
                self._version_picker.force_blockstate,
                self._picker.namespace,
                self._picker.name,
                properties,
            )
        else:
            self._property_picker = PropertySelect(
                self,
                translation_manager,
                self._version_picker.platform,
                self._version_picker.version_number,
                self._version_picker.force_blockstate,
                self._picker.namespace,
                self._picker.name,
                properties,
            )
        right_sizer.Add(self._property_picker, 1, wx.EXPAND)
        self._property_picker.Bind(EVT_PROPERTIES_CHANGE, self._on_property_change)

        self.SetSizerAndFit(self._sizer)
        self.Layout()

    @property
    def wildcard_mode(self) -> bool:
        """
        Is the UI in wildcard mode.
        If True multiple property values can be selected.
        These can be accessed through :attr:`extra_properties`
        """
        return self._wildcard_mode

    def _on_picker_change(self, evt):
        self._update_properties()
        evt.Skip()

    def _on_property_change(self, evt):
        self.Layout()
        evt.Skip()

    def _update_properties(self):
        self._property_picker.version_block = (
            self._version_picker.platform,
            self._version_picker.version_number,
            self._version_picker.force_blockstate,
            self._picker.namespace,
            self._picker.name,
        )

    @property
    def force_blockstate(self) -> bool:
        return self._version_picker.force_blockstate

    @force_blockstate.setter
    def force_blockstate(self, force_blockstate: bool):
        self._version_picker.force_blockstate = force_blockstate

    @property
    def block_name(self) -> str:
        return self._picker.name

    @block_name.setter
    def block_name(self, block_name: str):
        self._picker.name = block_name

    @property
    def properties(self) -> PropertyType:
        return self._property_picker.properties

    @properties.setter
    def properties(self, properties: PropertyType):
        self._property_picker.properties = properties



    @property
    def block(self) -> Block:
        return Block(self.namespace, self.block_name, self.properties)

    @block.setter
    def block(self, block: Block):
        self._picker.set_namespace(block.namespace)
        self._picker.set_name(block.base_name)
        self._update_properties()
        self.properties = block.properties

    @property
    def block_entity(self) -> Optional[BlockEntity]:
        return None  # TODO

    @block_entity.setter
    def block_entity(self, block_entity: Optional[BlockEntity]):
        if block_entity is not None:
            pass  # TODO

    @property
    def universal_block(self) -> Tuple[Block, Optional[BlockEntity]]:
        return self._translation_manager.get_version(
            self.platform, self.version_number
        ).block.to_universal(self.block, self.block_entity, self.force_blockstate)[:2]

    @universal_block.setter
    def universal_block(self, universal_block: Tuple[Block, Optional[BlockEntity]]):
        block, block_entity = universal_block
        v_block, v_block_entity = self._translation_manager.get_version(
            self.platform, self.version_number
        ).block.from_universal(block, block_entity, self.force_blockstate)[:2]
        if isinstance(v_block, Block):
            self.block = v_block
            self.block_entity = v_block_entity


def demo():
    """
    Show a demo version of the UI.
    An app instance must be created first.
    """
    translation_manager = PyMCTranslate.new_translation_manager()
    dialog = wx.Dialog(None, title="BlockDefine", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.DIALOG_NO_PARENT)
    sizer = wx.BoxSizer()
    dialog.SetSizer(sizer)
    sizer.Add(
        BlockDefine(dialog, translation_manager, wx.HORIZONTAL),
        1,
        wx.ALL | wx.EXPAND,
        5,
    )
    dialog.Show()
    dialog.Fit()
    dialog.Bind(wx.EVT_CLOSE, lambda evt: dialog.Destroy())


if __name__ == "__main__":

    def main():
        app = wx.App()
        demo()
        app.MainLoop()

    main()
