// Everything PortableKit has to be told about God of War: Chains of Olympus.
// The framework reads the rest out of the game's own executable.
//
// The numbers here were read off the player's disc, not recalled: the disc id
// and title from PSP_GAME/PARAM.SFO, the hashes from the files themselves, the
// tag from offset 0xD0 of EBOOT.BIN, and the load address and memory size from
// the ELF's program headers.

#include "profile.hpp"

#include "psprecomp/elf32.hpp"

#include <array>
#include <cstdint>

namespace portablekit {
namespace {

// The published 0x90-byte table for tag 0xC0CB167C, as little-endian words:
// the tag of the older "~PSP" header layout, which has no 16-byte key. The
// same table as Purun's (TeamGDB/Purun, MIT), whose game uses the same tag.
constexpr std::array<std::uint32_t, 36> kKeyTableWords = {
    0xDA8E36FAu, 0x5DD97447u, 0x76C19874u, 0x97E57EAFu, 0x1CAB09BDu, 0x9835BAC6u,
    0x03D39281u, 0x03B205CFu, 0x2882E734u, 0xE714F663u, 0xB96E2775u, 0xBD8AAFC7u,
    0x1DD3EC29u, 0xECA4A16Cu, 0x5F69EC87u, 0x85981E92u, 0x7CFCAE21u, 0xBAE9DD16u,
    0xE6A97804u, 0x2EEE02FCu, 0x61DF8A3Du, 0xDD310564u, 0x9697E149u, 0xC2453F3Bu,
    0xF91D8456u, 0x39DA6BC8u, 0xB3E5FEF5u, 0x89C593A3u, 0xFB5C8ABCu, 0x6C0B7212u,
    0xE10DD3CBu, 0x98D0B2A8u, 0x5FD61847u, 0xF0DC2357u, 0x7701166Au, 0x0F5C3B68u,
};

constexpr std::array<std::uint8_t, 0x90> key_table_bytes() {
    std::array<std::uint8_t, 0x90> bytes{};
    for (std::size_t i = 0; i < kKeyTableWords.size(); ++i)
        for (std::size_t b = 0; b < 4; ++b)
            bytes[i * 4 + b] = static_cast<std::uint8_t>(kKeyTableWords[i] >> (8 * b));
    return bytes;
}

constexpr std::array<std::uint8_t, 0x90> kKeyTable = key_table_bytes();

// The executable builds its save names at run time: the game name is the disc
// id, and the save names are its own. The trace shows it loading
// "UCES00842PROFILE00" at boot; its game saves are "DATA%02d" (the slots),
// not seen in a trace yet.
constexpr SaveFolder kSaveFolders[] = {
    {"UCES00842PROFILE00", "Profile", true},
    {"UCES00842DATA00", "Game data", true},
};

// The launcher: dark bronze, with Olympian gold. Its art is the player's,
// never the repository's: background.jpg and logo.jpg in <data>/launcher/
// when they put them there, else PIC1.PNG and ICON0.PNG from their disc image.
constexpr LauncherTheme kLauncher{
    .title = "GOD OF WAR",
    .subtitle = "CHAINS OF OLYMPUS",
    .background = 0x15130Fu,
    .sidebar = 0x0E0D0Au,
    .panel = 0x1D1A14u,
    .accent = 0xA8781Eu,
    .accent_bright = 0xD9A441u,
    .text = 0xEAE4D8u,
    .text_dim = 0x9E968Au,
    .backdrop_focus_y = 0.1f,
    .logo_on_black = true,
    .project_url = "https://github.com/arnaldolima1/gow-chains-of-olympus-pc",
    .issues_url = "https://github.com/arnaldolima1/gow-chains-of-olympus-pc/issues",
    .credits = "An unofficial port, played from your own copy of the game.",
};

} // namespace

const GameProfile &game() {
    static const GameProfile profile{
        .app_name = "OlympusNative",
        .project_name = "Olympus",
        .env_prefix = "OLYMPUS",
        .data_organization = "Olympus",
        .data_application = "UCES00842",

        .disc_id = "UCES00842",
        .disc_id_display = "UCES-00842",
        .game_title = "God of War: Chains of Olympus",
        .executable_path_on_disc = "PSP_GAME/SYSDIR/EBOOT.BIN",
        .param_sfo_path_on_disc = "PSP_GAME/PARAM.SFO",
        .release_name = "the European release (1.00)",
        // PSP_GAME/SYSDIR/EBOOT.BIN of the European release, and the
        // executable it decrypts to. (Its BOOT.BIN is all zeros.)
        .encrypted_executable_sha256 = "b5f1d9f77353fc57e6aa90b46b84eefbe295f9554a5f7bfb1699b1303eb1c438",
        .executable_sha256 = "a844a846b193cfb0fd6920264576553b0b0d981d1a8b9a6ffb3586402e7cd0cd",
        .decryption_tag = 0xC0CB167Cu,
        .decryption_key = {},
        .decryption_key_table = kKeyTable,

        .load_base = psprecomp::kDefaultPspUserLoadBase,
        .guest_ram_bytes = 32u * 1024u * 1024u,
        .boot_path = "disc0:/PSP_GAME/SYSDIR/EBOOT.BIN",
        .overlay_slots = {},

        .save_game_name = "UCES00842",
        .save_folders = kSaveFolders,

        .adhoc_product_code = "UCES00842",
        // The game has no multiplayer: no Network page.
        .adhoc_play = false,

        // As in Ghost of Sparta (the same engine), the frame loop waits only on
        // the GE: without this it flips about twice a vblank (120 game frames
        // a second at the title menu). At most one flip a vblank.
        .frame_vblanks = 1,
        .flips_wait_for_vblank = true,

        // A European console: English, confirm on cross.
        .system_language = 1u,
        .confirm_button = 1u,

        .launcher = &kLauncher,
    };
    return profile;
}

} // namespace portablekit
