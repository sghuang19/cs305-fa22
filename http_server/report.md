# CS305 Lab Assignment 1 Report

By Guanchao Huang, SID 11912309, from the School of Microelectronics. This
report serves as an explanation to the subtleties and hacks in the code.

## Subtleties

### Should I include `Content-Length` when no payload is sent?

For `404 Not Found` response, according to
[RFC9110](https://datatracker.ietf.org/doc/html/rfc9110#section-8.6):

> Aside from the cases defined above, in the absence of Transfer-Encoding, an
> origin server SHOULD send a Content-Length header field when the content size
> is known prior to sending the complete header section.

In this case, we know the size of the content is `0` at the first place, thus
`Content-Length: 0` should be included.

For `HEAD` requests, according to
[RFC9110](https://datatracker.ietf.org/doc/html/rfc9110#section-8.6):

> A server MAY send a Content-Length header field in a response to a HEAD
> request (Section 9.3.2); a server MUST NOT send Content-Length in such a
> response unless its field value equals the decimal number of octets that
> would have been sent in the content of a response if the same request had
> used the GET method.

Which is self-explanatory.

### Should I include `Content-Type` for `404 Not Found` response?

According to
[RFC2616](https://www.rfc-editor.org/rfc/rfc2616.html#section-7.2.1):

> Any HTTP/1.1 message containing an entity-body SHOULD include a Content-Type
> header field defining the media type of that body.

Note the use of the word *SHOULD*. The `Content-Type` field is not a *MUST*
even when content presents, not to mention in a `404` response with no content.

## Hacks

Most of the code are self-explanatory. The only hack involved is the conversion
from cookie string to json object.

```python
cookie_str = request.get_header('Cookie')
if cookie_str:
    # a hack converting cookie string to dict
    cookie_str = cookie_str.replace('; ', '", "').replace('=', '": "')
    cookies = json.loads('{"' + cookie_str + '"}')
else:
    cookies = {}
```

This follows from the fact that multiple cookie key-value pairs may present.
Defensive programming is used whenever needed.