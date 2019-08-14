import vtk

class SceneBrowser():
    def __init__(self,
                 scene_list={},
                 cameras=[],
                 labels={},
                 key_label_dict={},
                 show_description=True,
                 quit_key='q',
                 forward_key='Right',
                 backward_key='Left',
                 video_width=1080,
                 video_height=720):
        self._scene_list = scene_list
        self._key_label_dict = key_label_dict 

        if type(labels) is not dict and len(labels) == len(scene_list):
            labels = {ii:lbl for ii, lbl in enumerate(labels)} 
        self._labels = labels
        self.current_scene = 0

        self.video_width = video_width
        self.video_height = video_height
        self.iren = None
        self.ren = None
        self.renWin = None
        self.text_actor = None
        self.show_description = show_description
        self.quit_key = quit_key
        self.forward_key = forward_key
        self.backward_key = backward_key

    @property
    def labels(self):
        return self._labels

    def Launch(self, start_scene=None, back_color=(1,1,1)):
        if start_scene is not None:
            self.current_scene = start_scene
        self.vtk_callback(back_color=back_color)
        return

    def scene_forward(self):
        self.clear_window()
        self.current_scene = (self.current_scene + 1) % len(self._scene_list)
        self.update_scene()

    def scene_backward(self):
        self.clear_window()
        self.current_scene = (self.current_scene - 1) % len(self._scene_list)
        self.update_scene()

    def close_window(self):
        self.iren.TerminateApp()
        self.ren = None
        self.iren = None
        self.text_actor = None

    def clear_window(self):
        self.ren.RemoveActor(self.text_actor)
        for a in self._scene_list[self.current_scene]:
            self.ren.RemoveActor(a)

    def update_scene(self):
        for a in self._scene_list[self.current_scene]:
            self.ren.AddActor(a)
        if self.show_description:
            self.update_text()
        self.renWin.Render()

    def update_text(self):
        txt = 'Scene {}: Label ''{}'''.format(self.current_scene, self.labels.get(self.current_scene, 'None'))
        if len(self.labels) == len(self._scene_list) and len(self._key_label_dict) > 0:
            txt = txt + '  All scenes labeled!'
        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetInput(txt)
        self.text_actor.SetPosition2(10,40)
        self.text_actor.GetTextProperty().SetFontSize(24)
        self.text_actor.GetTextProperty().SetColor((0,0,0)) 
        self.ren.AddActor(self.text_actor)


    def vtk_callback(self, back_color=(1, 1, 1) ):
        def vtkKeyPress(obj, event):
            key = obj.GetKeySym()
            if key in self._key_label_dict:
                self._labels[self.current_scene] = self._key_label_dict[key]
                self.scene_forward()
            elif key == self.quit_key:
                self.close_window()
            elif key == self.forward_key:
                self.scene_forward()
            elif key == self.backward_key:
                self.scene_backward()
            return

        self.ren = vtk.vtkRenderer()
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.renWin.SetSize(self.video_width, self.video_height)
        self.ren.SetBackground(*back_color)

        self.update_scene()

        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        self.ren.ResetCamera()

        trackCamera = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(trackCamera)
        self.iren.AddObserver("KeyPressEvent", vtkKeyPress)

        self.iren.Initialize()
        self.iren.Render()
        self.iren.Start()
        self.renWin.Finalize()
        return
