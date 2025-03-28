import argparse
import deskapp


def main():
    parser = argparse.ArgumentParser(
                prog='Deskapp',
                description='A text based UI framework for Python.',
                epilog='Another Ruckusist.com Project.')
    
    # Add configuration options as command-line arguments
    # Basic configuration
    parser.add_argument('--name', type=str, default="Deskapp", help='Application name')
    parser.add_argument('--title', type=str, default="Demo Deskapp", help='Application title')
    parser.add_argument('--header', type=str, default="This is working.", help='Header text')
    parser.add_argument('--demo-mode', action='store_true', help='Enable demo mode with sample modules')
    parser.add_argument('--no-demo-mode', dest='demo_mode', action='store_false', help='Disable demo mode')
    parser.set_defaults(demo_mode=True)
    parser.add_argument('--splash-screen', action='store_true', help='Show splash screen on startup')

    # UI visibility options
    parser.add_argument('--show-header', action='store_true', dest='show_header', help='Show header')
    parser.add_argument('--hide-header', action='store_false', dest='show_header', help='Hide header')
    parser.add_argument('--show-footer', action='store_true', dest='show_footer', help='Show footer')
    parser.add_argument('--hide-footer', action='store_false', dest='show_footer', help='Hide footer')
    parser.add_argument('--show-menu', action='store_true', dest='show_menu', help='Show menu')
    parser.add_argument('--hide-menu', action='store_false', dest='show_menu', help='Hide menu')
    parser.add_argument('--show-messages', action='store_true', dest='show_messages', help='Show messages')
    parser.add_argument('--hide-messages', action='store_false', dest='show_messages', help='Hide messages')
    parser.add_argument('--show-box', action='store_true', dest='show_box', help='Show box')
    parser.add_argument('--hide-box', action='store_false', dest='show_box', help='Hide box')
    parser.add_argument('--show-banner', action='store_true', dest='show_banner', help='Show banner')
    parser.add_argument('--hide-banner', action='store_false', dest='show_banner', help='Hide banner')
    parser.set_defaults(show_header=True, show_footer=True, show_menu=True, 
                       show_messages=True, show_box=True, show_banner=True)

    # Disable options (prevent toggling)
    parser.add_argument('--disable-header', action='store_true', help='Disable header toggling')
    parser.add_argument('--disable-footer', action='store_true', help='Disable footer toggling')
    parser.add_argument('--disable-menu', action='store_true', help='Disable menu toggling')
    parser.add_argument('--disable-messages', action='store_true', help='Disable messages toggling')
    
    # Split configuration
    parser.add_argument('--v-split', type=float, default=0.4, help='Vertical split ratio (0.0-1.0)')
    parser.add_argument('--h-split', type=float, default=0.16, help='Horizontal split ratio (0.0-1.0)')
    
    # Mouse and focus options
    parser.add_argument('--use-mouse', action='store_true', help='Enable mouse support')
    parser.add_argument('--use-focus', action='store_true', help='Enable focus support')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the app with parsed arguments
    app = deskapp.App(
        name=args.name,
        title=args.title,
        header=args.header,
        demo_mode=args.demo_mode,
        splash_screen=args.splash_screen,
        
        # UI visibility options
        show_header=args.show_header,
        show_footer=args.show_footer,
        show_menu=args.show_menu,
        show_messages=args.show_messages,
        show_box=args.show_box,
        show_banner=args.show_banner,
        
        # Disable options
        disable_header=args.disable_header,
        disable_footer=args.disable_footer,
        disable_menu=args.disable_menu,
        disable_messages=args.disable_messages,
        
        # Split configuration
        v_split=args.v_split,
        h_split=args.h_split,
        
        # Mouse and focus options
        use_mouse=args.use_mouse,
        use_focus=args.use_focus,
        
        # Default empty modules list
        modules=[]
    )
    
    # App is automatically started due to autostart=True by default


if __name__ == "__main__":
    main()
