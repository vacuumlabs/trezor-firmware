use crate::ui::geometry::Rect;

use super::{Canvas, DrawingCache, Renderer, Shape, ShapeClone};

use without_alloc::alloc::LocalAllocLeakExt;

pub struct Blurring {
    // Blurred area
    area: Rect,
    /// Blurring kernel radius
    radius: usize,
}

/// A shape for the blurring of a specified rectangle area.
impl Blurring {
    pub fn new(area: Rect, radius: usize) -> Self {
        Self { area, radius }
    }

    pub fn render<'s>(self, renderer: &mut impl Renderer<'s>) {
        renderer.render_shape(self);
    }
}

impl Shape<'_> for Blurring {
    fn bounds(&self) -> Rect {
        self.area
    }

    fn cleanup(&mut self, _cache: &DrawingCache) {}

    fn draw(&mut self, canvas: &mut dyn Canvas, cache: &DrawingCache) {
        canvas.blur_rect(self.area, self.radius, cache);
    }
}

impl<'s> ShapeClone<'s> for Blurring {
    fn clone_at_bump<T>(self, bump: &'s T) -> Option<&'s mut dyn Shape<'s>>
    where
        T: LocalAllocLeakExt<'s>,
    {
        let clone = bump.alloc_t()?;
        Some(clone.uninit.init(Blurring { ..self }))
    }
}
