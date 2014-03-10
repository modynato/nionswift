# standard libraries
import logging
import unittest
import weakref

# third party libraries
import numpy
import scipy

# local libraries
from nion.imaging import Image
from nion.swift import Application
from nion.swift import DataGroup
from nion.swift import DataItem
from nion.swift import DocumentController
from nion.swift import DocumentModel
from nion.swift import ImagePanel
from nion.swift import Storage
from nion.ui import Test
from nion.ui import UserInterface


def construct_test_document(app, workspace_id=None):
    datastore = Storage.DictDatastore()
    document_model = DocumentModel.DocumentModel(datastore)
    document_controller = DocumentController.DocumentController(app.ui, document_model, workspace_id=workspace_id)
    data_group1 = DataGroup.DataGroup()
    document_model.data_groups.append(data_group1)
    data_item1a = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
    document_model.append_data_item(data_item1a)
    data_group1.append_data_item(data_item1a)
    data_item1b = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
    document_model.append_data_item(data_item1b)
    data_group1.append_data_item(data_item1b)
    data_group1a = DataGroup.DataGroup()
    data_group1.data_groups.append(data_group1a)
    data_group1b = DataGroup.DataGroup()
    data_group1.data_groups.append(data_group1b)
    data_group2 = DataGroup.DataGroup()
    document_controller.document_model.data_groups.append(data_group2)
    data_group2a = DataGroup.DataGroup()
    data_group2.data_groups.append(data_group2a)
    data_group2b = DataGroup.DataGroup()
    data_group2.data_groups.append(data_group2b)
    data_group2b1 = DataGroup.DataGroup()
    data_group2b.data_groups.append(data_group2b1)
    data_item2b1a = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
    document_model.append_data_item(data_item2b1a)
    data_group2b1.append_data_item(data_item2b1a)
    return document_controller

class TestDocumentControllerClass(unittest.TestCase):

    def setUp(self):
        self.app = Application.Application(Test.UserInterface(), set_global=False)

    def tearDown(self):
        pass

    def test_delete_document_controller(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model)
        document_model = None
        weak_document_model = weakref.ref(document_controller.document_model)
        weak_document_window = weakref.ref(document_controller.document_window)
        weak_document_controller = weakref.ref(document_controller)
        self.assertIsNotNone(weak_document_controller())
        self.assertIsNotNone(weak_document_window())
        self.assertIsNotNone(weak_document_model())
        document_controller.close()
        document_controller = None
        self.assertIsNone(weak_document_controller())
        self.assertIsNone(weak_document_window())
        self.assertIsNone(weak_document_model())

    def test_image_panel_releases_data_item(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model)
        data_item = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        document_model.append_data_item(data_item)
        weak_data_item = weakref.ref(data_item)
        image_panel = ImagePanel.ImagePanel(document_controller, "image-panel", {})
        image_panel.data_item = data_item
        self.assertIsNotNone(weak_data_item())
        image_panel.close()
        document_controller.close()
        document_controller = None
        data_item = None
        document_model = None
        self.assertIsNone(weak_data_item())

    def test_flat_data_groups(self):
        document_controller = construct_test_document(self.app)
        self.assertEqual(len(list(document_controller.document_model.get_flat_data_group_generator())), 7)
        self.assertEqual(len(list(document_controller.document_model.get_flat_data_item_generator())), 3)
        self.assertEqual(document_controller.document_model.get_data_item_by_key(0), document_controller.document_model.data_groups[0].data_items[0])
        self.assertEqual(document_controller.document_model.get_data_item_by_key(1), document_controller.document_model.data_groups[0].data_items[1])
        self.assertEqual(document_controller.document_model.get_data_item_by_key(2), document_controller.document_model.data_groups[1].data_groups[1].data_groups[0].data_items[0])

    def test_receive_files_should_put_files_into_document_model_at_end(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        data_item1 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item1.title = "data_item1"
        document_model.append_data_item(data_item1)
        data_item2 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item2.title = "data_item2"
        document_model.append_data_item(data_item2)
        data_item3 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item3.title = "data_item3"
        document_model.append_data_item(data_item3)
        new_data_items = document_controller.receive_files([":/app/scroll_gem.png"], external=False, threaded=False)
        self.assertEqual(document_model.data_items.index(new_data_items[0]), 3)

    def test_receive_files_should_put_files_into_document_model_at_index(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        data_item1 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item1.title = "data_item1"
        document_model.append_data_item(data_item1)
        data_item2 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item2.title = "data_item2"
        document_model.append_data_item(data_item2)
        data_item3 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item3.title = "data_item3"
        document_model.append_data_item(data_item3)
        new_data_items = document_controller.receive_files([":/app/scroll_gem.png"], index=2, external=False, threaded=False)
        self.assertEqual(document_model.data_items.index(new_data_items[0]), 2)

    def test_receive_files_should_put_files_into_data_group_at_index(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        data_group = DataGroup.DataGroup()
        document_model.data_groups.append(data_group)
        data_item1 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item1.title = "data_item1"
        document_model.append_data_item(data_item1)
        data_group.append_data_item(data_item1)
        data_item2 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item2.title = "data_item2"
        document_model.append_data_item(data_item2)
        data_group.append_data_item(data_item2)
        data_item3 = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        data_item3.title = "data_item3"
        document_model.append_data_item(data_item3)
        data_group.append_data_item(data_item3)
        new_data_items = document_controller.receive_files([":/app/scroll_gem.png"], data_group=data_group, index=2, external=False, threaded=False)
        self.assertEqual(document_model.data_items.index(new_data_items[0]), 3)
        self.assertEqual(data_group.data_items.index(new_data_items[0]), 2)

    def test_remove_graphic_removes_it_from_data_item(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        data_item = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        document_model.append_data_item(data_item)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        image_panel = document_controller.selected_image_panel
        image_panel.data_item = data_item
        line_graphic = document_controller.add_line_graphic()
        # make sure assumptions are correct
        self.assertEqual(len(image_panel.graphic_selection.indexes), 1)
        self.assertTrue(0 in image_panel.graphic_selection.indexes)
        self.assertEqual(len(data_item.graphics), 1)
        self.assertEqual(data_item.graphics[0], line_graphic)
        # remove the graphic and make sure things are as expected
        document_controller.remove_graphic()
        self.assertEqual(len(image_panel.graphic_selection.indexes), 0)
        self.assertEqual(len(data_item.graphics), 0)
        # clean up
        image_panel.close()

    def test_remove_line_profile_removes_associated_child_data_item(self):
        datastore = Storage.DictDatastore()
        document_model = DocumentModel.DocumentModel(datastore)
        data_item = DataItem.DataItem(numpy.zeros((256, 256), numpy.uint32))
        document_model.append_data_item(data_item)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        image_panel = document_controller.selected_image_panel
        line_profile_data_item = document_controller.processing_line_profile()
        line_profile_operation = line_profile_data_item.operations[0]
        image_panel.data_item = data_item
        image_panel.graphic_selection.clear()
        image_panel.graphic_selection.add(0)
        # make sure assumptions are correct
        self.assertEqual(len(data_item.data_items), 1)
        self.assertTrue(line_profile_operation.graphics[0] in data_item.drawn_graphics)
        # remove the graphic and make sure things are as expected
        document_controller.remove_graphic()
        self.assertEqual(len(image_panel.graphic_selection.indexes), 0)  # disabled until test_remove_line_profile_updates_graphic_selection
        self.assertEqual(len(data_item.drawn_graphics), 0)
        self.assertEqual(len(data_item.data_items), 0)
        # clean up
        image_panel.close()

    def test_remove_line_profile_updates_graphic_selection(self):
        # TODO: enable line in test_remove_line_profile_removes_associated_child_data_item
        pass


if __name__ == '__main__':
    unittest.main()
