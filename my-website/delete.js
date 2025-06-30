body {
    color: #fff
}

h1 {
    font-size: 4rem;
    line-height: 120%;
    letter-spacing: .01rem
}

@media(max-width: 1600px) {
    h1 {
        font-size:3.5rem
    }
}

@media(max-width: 1024px) {
    h1 {
        font-size:2.25rem
    }
}

@media(max-width: 576px) {
    h1 {
        font-size:2.25rem
    }
}

h1 strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

h2 {
    font-size: 3.5rem;
    line-height: 120%;
    letter-spacing: 0
}

@media(max-width: 1600px) {
    h2 {
        font-size:3rem
    }
}

@media(max-width: 1024px) {
    h2 {
        font-size:2rem
    }
}

@media(max-width: 576px) {
    h2 {
        font-size:2rem
    }
}

h2 strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

h3 {
    font-size: 2.75rem;
    line-height: 125%;
    letter-spacing: .01rem
}

@media(max-width: 1600px) {
    h3 {
        font-size:2.25rem
    }
}

@media(max-width: 1024px) {
    h3 {
        font-size:1.75rem
    }
}

@media(max-width: 576px) {
    h3 {
        font-size:1.5rem
    }
}

h3 strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

h4 {
    font-size: 2.25rem;
    line-height: 125%;
    letter-spacing: .02rem
}

@media(max-width: 1600px) {
    h4 {
        font-size:1.875rem
    }
}

@media(max-width: 1024px) {
    h4 {
        font-size:1.5rem
    }
}

@media(max-width: 576px) {
    h4 {
        font-size:1.375rem
    }
}

h4 strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

h5 {
    font-size: 2rem;
    line-height: 125%;
    letter-spacing: .02rem;
    font-weight: 500
}

@media(max-width: 1600px) {
    h5 {
        font-size:1.75rem
    }
}

@media(max-width: 1024px) {
    h5 {
        font-size:1.375rem
    }
}

@media(max-width: 576px) {
    h5 {
        font-size:1.375rem
    }
}

h5 strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

h6 {
    font-size: 1.75rem;
    line-height: 125%;
    letter-spacing: .02rem
}

@media(max-width: 1600px) {
    h6 {
        font-size:1.5rem
    }
}

@media(max-width: 1024px) {
    h6 {
        font-size:1.25rem
    }
}

@media(max-width: 576px) {
    h6 {
        font-size:1.25rem
    }
}

h6 strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

p {
    font-size: 1.25rem;
    line-height: 145%;
    letter-spacing: .04rem
}

@media(max-width: 1600px) {
    p {
        font-size:1.125rem
    }
}

@media(max-width: 1024px) {
    p {
        font-size:1.125rem
    }
}

@media(max-width: 576px) {
    p {
        font-size:1rem
    }
}

p strong {
    font-size: inherit;
    font-weight: inherit;
    color: #5499ff
}

p.banner,p.large {
    font-size: 1.375rem;
    line-height: 150%;
    letter-spacing: .01rem
}

@media(max-width: 1600px) {
    p.banner,p.large {
        font-size:1.25rem
    }
}

@media(max-width: 1024px) {
    p.banner,p.large {
        font-size:1.125rem
    }
}

@media(max-width: 576px) {
    p.banner,p.large {
        font-size:1rem
    }
}

a {
    text-decoration: unset
}

main {
    position: relative;
    transition: margin-top .6s ease-in-out
}

html.top-banner-active main {
    margin-top: var(--bannerHeightTop,177px)
}

@keyframes growToPosition {
    0% {
        opacity: 0;
        transform: translateX(-24px) scale(.5)
    }

    to {
        opacity: 1;
        transform: translateX(0) scale(1)
    }
}

@keyframes shrinkAndFade {
    0% {
        opacity: 1;
        transform: translateX(0) scale(1)
    }

    to {
        opacity: 0;
        transform: translateX(24px) scale(.5)
    }
}

.Footer {
    background: #000;
    backdrop-filter: blur(15px);
    display: flex;
    flex-direction: column
}

.Footer--wrapper {
    width: 90%;
    max-width: 1600px;
    margin: 0 auto
}

.Footer--top {
    display: flex;
    justify-content: space-between;
    padding: 3.75rem 0
}

.Footer--top .logo {
    width: 10.125rem
}

.Footer--nav {
    display: flex;
    justify-content: space-between;
    flex: 1;
    margin: 0 5rem
}

.Footer--nav .nav-box {
    width: 25%
}

.Footer--nav .nav-box .column-header {
    color: #ebeced;
    font-size: .875rem;
    font-weight: 500;
    line-height: 130%;
    letter-spacing: .0163rem;
    text-decoration: none
}

.Footer--nav .nav-box .column-subnav {
    margin-top: 1rem
}

.Footer--nav .nav-box .nav-item {
    margin-bottom: .625rem
}

.Footer--nav .nav-box .nav-item:last-child {
    margin-bottom: unset
}

.Footer--nav .nav-box .nav-item a {
    color: #dee0e1;
    font-size: .875rem;
    font-style: normal;
    line-height: 150%;
    letter-spacing: .0163rem;
    text-decoration: none;
    opacity: .7
}

@media(min-width: 1600px) {
    .Footer--nav .nav-box .nav-item a {
        font-size:16px;
        line-height: 200%
    }
}

@media(max-width: 576px) {
    .Footer--nav .nav-box .nav-item a {
        font-size:13px
    }
}

.Footer--nav .nav-box .nav-item a:focus,.Footer--nav .nav-box .nav-item a:hover {
    background-color: transparent!important;
    opacity: 1
}

.Footer--nav .nav-box #ot-sdk-btn.ot-sdk-show-settings {
    color: #d7dfed;
    font-size: .875rem;
    font-style: normal;
    line-height: 150%;
    letter-spacing: .0163rem;
    text-decoration: none;
    opacity: .7;
    border: none;
    padding: 0;
    text-align: left;
    text-transform: lowercase
}

.Footer--nav .nav-box #ot-sdk-btn.ot-sdk-show-settings:first-letter {
    text-transform: uppercase
}

@media(max-width: 576px) {
    .Footer--nav .nav-box #ot-sdk-btn.ot-sdk-show-settings {
        font-size:13px
    }
}

@media(min-width: 1600px) {
    .Footer--nav .nav-box #ot-sdk-btn.ot-sdk-show-settings {
        font-size:16px;
        line-height: 200%
    }
}

.Footer--nav .nav-box #ot-sdk-btn.ot-sdk-show-settings:focus,.Footer--nav .nav-box #ot-sdk-btn.ot-sdk-show-settings:hover {
    background-color: transparent!important;
    opacity: 1
}

.Footer .social-wrap {
    display: flex
}

.Footer .social-wrap .mobile {
    display: none
}

.Footer--bottom {
    text-align: center;
    padding: 1.25rem 0;
    border-top: 1px solid #3e454f
}

.Footer--bottom .copyright-text {
    color: #b1b4b8;
    font-size: .875rem;
    line-height: 130%;
    letter-spacing: .0163rem
}

@media(max-width: 576px) {
    .Footer--bottom .copyright-text {
        font-size:13px
    }
}

@media(max-width: 1024px) {
    .Footer--top {
        flex-wrap:wrap
    }

    .Footer--nav {
        flex: unset;
        margin: 3rem 0;
        width: 100%
    }
}

@media(max-width: 576px) {
    .Footer--nav {
        flex-wrap:wrap;
        row-gap: 1.5rem
    }

    .Footer--nav .nav-box {
        width: 50%
    }
}

#onetrust-consent-sdk #ot-sdk-btn-floating {
    display: none
}

#onetrust-consent-sdk #onetrust-banner-sdk {
    background-color: rgba(48,58,66,.6)!important;
    backdrop-filter: blur(20px)!important;
    -webkit-backdrop-filter: blur(20px)!important
}

#onetrust-consent-sdk #onetrust-banner-sdk .onetrust-close-btn-container {
    top: 0;
    right: 0
}

@media(min-width: 1024px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-row {
        display:flex;
        align-items: center
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-eight.ot-sdk-columns {
    width: 55%
}

@media(max-width: 1023px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-eight.ot-sdk-columns {
        width:90%;
        margin-bottom: 30px
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container {
    padding-top: clamp(1px,calc(30vw * (100 / var(--siteBasis))),calc(30px * var(--siteMax) / var(--siteBasis)));
    padding-bottom: clamp(1px,calc(50vw * (100 / var(--siteBasis))),calc(50px * var(--siteMax) / var(--siteBasis)))
}

@media(max-width: 1023px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container {
        padding:30px 20px 50px
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-policy {
    margin-block:0}

@media(max-width: 896px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-policy {
        margin-left:0
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-policy-text {
    color: hsla(0,0%,100%,.6);
    font-size: clamp(1px,calc(16vw * (100 / var(--siteBasis))),calc(16px * var(--siteMax) / var(--siteBasis)));
    font-style: normal;
    font-weight: 400;
    line-height: 130%;
    letter-spacing: clamp(1px,calc(.32vw * (100 / var(--siteBasis))),calc(.32px * var(--siteMax) / var(--siteBasis)))
}

@media(max-width: 1023px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-policy-text {
        font-size:16px
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-consent-sdk #onetrust-banner-sdk :focus,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-consent-sdk #onetrust-banner-sdk:focus {
    outline-color: transparent;
    outline-width: 1px
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group {
    align-items: center;
    display: flex;
    flex-direction: row;
    margin-top: 0
}

@media(max-width: 1023px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group {
        display:flex;
        flex-direction: row-reverse;
        justify-content: flex-end
    }
}

@media(min-width: 890px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group button {
        margin-bottom:0
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-pc-btn-handler {
    color: #fff;
    text-align: center;
    font-size: clamp(1px,calc(14vw * (100 / var(--siteBasis))),calc(14px * var(--siteMax) / var(--siteBasis)));
    font-style: normal;
    font-weight: 500;
    line-height: 95.9%;
    letter-spacing: clamp(1px,calc(.56vw * (100 / var(--siteBasis))),calc(.56px * var(--siteMax) / var(--siteBasis)));
    text-decoration-line: underline;
    border-color: transparent;
    background-color: transparent;
    position: relative;
    width: fit-content
}

@media(max-width: 1023px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-pc-btn-handler {
        font-size:12px;
        width: 25%
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler {
    background-color: #297fff;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.15rem 1.75rem;
    font-family: helvetica-now-display,sans-serif,-apple-system,BlinkMacSystemFont,Apple Color Emoji,Segoe UI,Segoe UI Emoji,Segoe UI Symbol;
    font-weight: 500;
    font-size: .9375rem;
    line-height: 95.9%;
    color: #fff;
    cursor: pointer;
    border: 1.6px solid #297fff;
    transition: box-shadow .3s ease,transform .3s ease,background-color .3s ease;
    position: relative;
    overflow: hidden;
    padding: .88rem 1.25rem!important;
    min-width: unset;
    width: fit-content
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.size--small,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.size--small {
    padding: .88rem 1.25rem;
    font-weight: 400;
    line-height: 95.9%;
    font-size: 15px
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.shape--rounded,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.shape--rounded {
    border-radius: 4px
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.type--outlined,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.type--outlined {
    border: 1.6px solid #fff
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.type--borderless,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.type--borderless {
    border: unset;
    background-color: transparent;
    padding: unset
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.color--secondary,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.color--secondary {
    background-color: transparent
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.color--secondary:hover,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.color--secondary:hover {
    box-shadow: unset;
    background-color: hsla(0,0%,100%,.24);
    transition: background-color .3s ease
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler.with-icon span,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler.with-icon span {
    margin-right: 8px
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler .icon-wrapper,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler .icon-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 1.5rem;
    width: 1.5rem
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler .icon-1,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler .icon-2,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler .icon-1,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler .icon-2 {
    position: absolute;
    display: block
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler .icon-1,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler .icon-1 {
    opacity: 0;
    transform: translateX(-24px) scale(.5)
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler .icon-2,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler .icon-2 {
    transition: transform .5s ease,opacity .5s ease
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler:hover,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler:hover {
    box-shadow: 0 4px 40px 0 rgba(84,153,255,.56)
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler:hover .icon-1,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler:hover .icon-1 {
    animation: growToPosition .5s forwards
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler:hover .icon-2,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler:hover .icon-2 {
    animation: shrinkAndFade .5s forwards
}

@media(max-width: 1024px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler {
        padding:1rem 1.5rem;
        font-size: 1rem
    }
}

@media(max-width: 576px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler {
        padding:.875rem 1.25rem;
        font-size: .875rem
    }
}

@media(min-width: 1600px) {
    #onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler {
        font-size:1.125rem
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler:hover,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler:hover {
    opacity: 1
}

#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-accept-btn-handler:after,#onetrust-consent-sdk #onetrust-banner-sdk .ot-sdk-container #onetrust-button-group #onetrust-reject-all-handler:after {
    display: none!important
}

#onetrust-pc-sdk div #accept-recommended-btn-handler,#onetrust-pc-sdk div .ot-pc-refuse-all-handler,#onetrust-pc-sdk div .save-preference-btn-handler {
    border-radius: 3px;
    background-color: #297fff!important;
    border-color: #297fff!important
}

#onetrust-pc-sdk div .privacy-notice-link {
    text-decoration: none;
    border: none
}

@media(max-width: 1023px) {
    #onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent {
        display:flex;
        width: 100%;
        position: static;
        transform: none
    }
}

#onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent button {
    margin-top: 0;
    margin-bottom: 0
}

#onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent button:not(#onetrust-pc-btn-handler) {
    border-width: 2px;
    border-radius: 3px;
    display: flex;
    align-items: center
}

#onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent button:not(#onetrust-pc-btn-handler):after {
    content: "";
    display: inline-block;
    background-image: url(/assets/images/components/Cookies/banner-carrot.svg);
    background-size: contain;
    background-repeat: no-repeat;
    height: 14px;
    width: 8px;
    margin-left: 10px
}

@media(min-width: 1024px)and (max-width:1200px) {
    #onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent.has-reject-all-button {
        margin-left:5px
    }
}

@media(max-width: 499px) {
    #onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent.has-reject-all-button button:not(:last-of-type) {
        margin-bottom:1em
    }

    #onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent.has-reject-all-button #onetrust-button-group {
        flex-wrap: wrap;
        width: 100%
    }
}

@media(max-width: 1024px) {
    #onetrust-consent-sdk #onetrust-banner-sdk.otFlat #onetrust-button-group-parent.has-reject-all-button #onetrust-pc-btn-handler {
        width:fit-content;
        font-size: 14px
    }
}

@media only screen and (min-width: 1024px) {
    #onetrust-banner-sdk:not(.ot-iab-2) #onetrust-button-group-parent {
        margin:auto;
        width: 45%!important
    }
}
