def render_certificate_svg(certificate) -> str:
    registration = certificate.registration
    participant = registration.participant
    event = registration.event
    issued_label = certificate.issued_at.strftime("%d %B %Y")

    def esc(value: str) -> str:
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100" role="img" aria-label="Certificate">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#e2e8f0"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f766e"/>
      <stop offset="100%" stop-color="#115e59"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="1100" fill="url(#bg)"/>
  <rect x="36" y="36" width="1528" height="1028" rx="28" fill="#ffffff" stroke="#cbd5e1" stroke-width="4"/>
  <rect x="70" y="70" width="1460" height="960" rx="22" fill="none" stroke="#0f766e" stroke-width="2" stroke-dasharray="10 8"/>
  <circle cx="180" cy="170" r="70" fill="#ccfbf1"/>
  <circle cx="1420" cy="930" r="90" fill="#cffafe"/>
  <text x="800" y="170" text-anchor="middle" font-family="Georgia, serif" font-size="34" fill="#0f766e" letter-spacing="8">ITTS COMMUNITY</text>
  <text x="800" y="255" text-anchor="middle" font-family="Georgia, serif" font-size="74" fill="#0f172a">Certificate of Completion</text>
  <rect x="570" y="295" width="460" height="8" rx="4" fill="url(#accent)"/>
  <text x="800" y="390" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" fill="#475569">This certificate is proudly awarded to</text>
  <text x="800" y="500" text-anchor="middle" font-family="Georgia, serif" font-size="72" fill="#0f172a">{esc(participant.name)}</text>
  <text x="800" y="575" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" fill="#475569">for successfully participating in the webinar</text>
  <text x="800" y="665" text-anchor="middle" font-family="Georgia, serif" font-size="48" fill="#115e59">{esc(event.title)}</text>
  <text x="800" y="735" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#64748b">Issued on {esc(issued_label)}</text>
  <rect x="140" y="830" width="430" height="120" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="175" y="878" font-family="Arial, sans-serif" font-size="18" fill="#64748b">Certificate Number</text>
  <text x="175" y="920" font-family="Arial, sans-serif" font-size="28" fill="#0f172a">{esc(certificate.certificate_number)}</text>
  <rect x="1030" y="830" width="430" height="120" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="1065" y="878" font-family="Arial, sans-serif" font-size="18" fill="#64748b">Verified Recipient</text>
  <text x="1065" y="920" font-family="Arial, sans-serif" font-size="28" fill="#0f172a">{esc(participant.email)}</text>
  <line x1="640" y1="920" x2="960" y2="920" stroke="#94a3b8" stroke-width="3"/>
  <text x="800" y="955" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#475569">Authorized by Webinar ITTS</text>
</svg>"""
