###############################################################################################################################################
# STEP 1:            Not my code, Author: ODTitan
# Install Pip 10.4: (pip install Pillow==10.4)
# In the /.venv/Lib/site-packages/moviepy/video/compositing/CompositeVideoClip.py, replace the make_frame function with the following code:
###############################################################################################################################################
        def make_frame(t):
            full_w, full_h = self.bg.size
            f = self.bg.get_frame(t).astype('uint8')
            bg_im = Image.fromarray(f)
            for c in self.playing_clips(t):
                img, pos, mask, ismask = c.new_blit_on(t, f)

                x, y = pos
                w, h = c.size

                out_x = x < -w or x == full_w
                out_y = y < -h or y == full_h

                if out_x and out_y:
                    continue

                pos = (int(round(min(max(-w, x), full_w))),
                       int(round(min(max(-h, y), full_h))))

                paste_im = Image.fromarray(img)

                if mask is not None:
                    mask_im = Image.fromarray(255 * mask).convert('L')
                    bg_im.paste(paste_im, pos, mask_im)
                else:
                    bg_im.paste(paste_im, pos)

            result_frame = np.array(bg_im)

            return result_frame.astype('uint8') if (not ismask) else result_frame

        self.make_frame = make_frame

###############################################################################################################################################
# STEP 2:
# In the /.venv/Lib/site-packages/moviepy/video/VideoClip.py, add the following code below the def blit_on(self, picture, t) function:
###############################################################################################################################################

    # New Fast Blit On method
    def new_blit_on(self, t, picture):
        hf, wf = framesize = picture.shape[:2]

        if self.ismask and picture.max() != 0:
            return np.minimum(1, picture + self.blit_on(np.zeros(framesize), t))

        ct = t - self.start  # clip time

        img = self.get_frame(ct) #Get Image Mask
        mask = (None if (self.mask is None) else
                self.mask.get_frame(ct))
        if mask is not None:
            if (img.shape[0] != mask.shape[0]) or (img.shape[1] != mask.shape[1]):
                img = self.fill_array(img, mask.shape)
        hi, wi = img.shape[:2]

        pos = self.pos(ct) #Set Position

        # preprocess short writings of the position
        if isinstance(pos, str):
            pos = {'center': ['center', 'center'],
                   'left': ['left', 'center'],
                   'right': ['right', 'center'],
                   'top': ['center', 'top'],
                   'bottom': ['center', 'bottom']}[pos]
        else:
            pos = list(pos)

        # is the position relative (given in % of the clip's size) ?
        if self.relative_pos:
            for i, dim in enumerate([wf, hf]):
                if not isinstance(pos[i], str):
                    pos[i] = dim * pos[i]

        if isinstance(pos[0], str):
            D = {'left': 0, 'center': (wf - wi) / 2, 'right': wf - wi}
            pos[0] = D[pos[0]]

        if isinstance(pos[1], str):
            D = {'top': 0, 'center': (hf - hi) / 2, 'bottom': hf - hi}
            pos[1] = D[pos[1]]

        return img, pos, mask, self.ismask
