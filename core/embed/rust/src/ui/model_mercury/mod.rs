use super::{geometry::Rect, UIFeaturesCommon};

#[cfg(feature = "bootloader")]
pub mod bootloader;
pub mod component;
pub mod constant;
pub mod theme;

mod screens;

pub struct ModelMercuryFeatures;

impl UIFeaturesCommon for ModelMercuryFeatures {
    fn fadein() {
        #[cfg(feature = "backlight")]
        crate::ui::display::fade_backlight_duration(theme::BACKLIGHT_NORMAL, 150);
    }

    fn fadeout() {
        #[cfg(feature = "backlight")]
        crate::ui::display::fade_backlight_duration(theme::BACKLIGHT_DIM, 150);
    }

    fn backlight_on() {
        #[cfg(feature = "backlight")]
        crate::ui::display::set_backlight(theme::BACKLIGHT_NORMAL);
    }

    const SCREEN: Rect = constant::SCREEN;

    fn screen_fatal_error(title: &str, msg: &str, footer: &str) {
        screens::screen_fatal_error(title, msg, footer);
    }

    fn screen_boot_stage_2() {
        screens::screen_boot_stage_2();
    }
}
