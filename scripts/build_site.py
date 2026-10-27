#!/usr/bin/env python3
"""Local static production build; does not deploy anything."""
import build_blog
import build_i18n
build_blog.main()
build_i18n.main()
