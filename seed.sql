--
-- PostgreSQL database dump
--

\restrict Do2jPGxGe31kwY1AqZqkaE6xf5MnV76MBjlyhQym5URRcFQly3xjhZ0tgekvq49

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-08-01 09:41:33

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4942 (class 0 OID 16584)
-- Dependencies: 222
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.categories VALUES (1, 'Arabica', 'Biji kopi 100% Arabica', true, '2026-07-31 22:01:53.965625');
INSERT INTO public.categories VALUES (2, 'Robusta', 'Biji kopi 100% Robusta', true, '2026-07-31 22:01:53.965625');
INSERT INTO public.categories VALUES (3, 'Blend', 'Biji kopi 50% Arabica 50% Robusta', true, '2026-07-31 22:01:53.965625');
INSERT INTO public.categories VALUES (4, 'Liberica', 'Biji kopi 100% Liberica', true, '2026-07-31 22:01:53.965625');
INSERT INTO public.categories VALUES (5, 'Excelsa', 'Biji kopi 100% Excelsa', true, '2026-07-31 22:01:53.965625');


--
-- TOC entry 4940 (class 0 OID 16563)
-- Dependencies: 220
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users VALUES (1, 'Budi', 'budi123@email.com', 'password123', true, '2026-07-31 13:22:26.345015');
INSERT INTO public.users VALUES (2, 'Andi', 'andi123@email.com', 'wordpass123', true, '2026-07-31 13:22:26.345015');
INSERT INTO public.users VALUES (3, 'Dika', 'dika456@email.com', 'rahasi123', true, '2026-07-31 13:22:26.345015');
INSERT INTO public.users VALUES (4, 'Abdul', 'abdul789@email.com', 'apaantuh456', true, '2026-07-31 13:22:26.345015');
INSERT INTO public.users VALUES (5, 'Joko', 'joko666@email.com', 'xixixi555', true, '2026-07-31 13:22:26.345015');


--
-- TOC entry 4946 (class 0 OID 16620)
-- Dependencies: 226
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.orders VALUES (1, 2, 94000.00, 'pending', '2026-08-01 09:26:01.526887');
INSERT INTO public.orders VALUES (2, 1, 85000.00, 'processing', '2026-08-01 09:26:01.526887');
INSERT INTO public.orders VALUES (3, 4, 80000.00, 'delivering', '2026-08-01 09:26:01.526887');
INSERT INTO public.orders VALUES (4, 3, 100000.00, 'pending', '2026-08-01 09:26:01.526887');


--
-- TOC entry 4944 (class 0 OID 16599)
-- Dependencies: 224
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.products VALUES (1, 'Arabica Sidikalang', 1, 'Flavor Notes: Spices, Cinnamon, Lemon zest. Netto 200 gram', 85000.00, 50, '2026-07-31 22:16:42.944873');
INSERT INTO public.products VALUES (2, 'Arabica Mandailing', 1, 'Flavor Notes: Malt, Nutty, Bitter Sweet, Floral. Netto 200 gram', 94000.00, 50, '2026-07-31 22:16:42.944873');
INSERT INTO public.products VALUES (3, 'Robusta Lampung', 2, 'Flavor Notes: Dark cocoa, Nutty, Caramelized. Netto 200 gram', 65000.00, 70, '2026-07-31 22:16:42.944873');
INSERT INTO public.products VALUES (4, 'Excelsa Muria', 5, 'Flavor Notes: Chocolate, Floral, Brown Sugar. Netto 200 gram', 40000.00, 20, '2026-07-31 22:16:42.944873');
INSERT INTO public.products VALUES (5, 'Little Sweet Liberica', 4, 'Flavor Notes: Fruity, Nutty, Sweet, Spicy, Smoky, Little Bit of Mint. Netto 200 gram', 100000.00, 60, '2026-07-31 22:16:42.944873');
INSERT INTO public.products VALUES (6, 'Italian Blend', 3, 'Flavor Notes: Brown Sugar, Sweet, Strong, Chocolate. Netto 200 gram', 80000.00, 90, '2026-07-31 22:16:42.944873');


--
-- TOC entry 4947 (class 0 OID 16639)
-- Dependencies: 227
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.order_items VALUES (1, 2, 1);
INSERT INTO public.order_items VALUES (2, 1, 1);
INSERT INTO public.order_items VALUES (3, 6, 1);
INSERT INTO public.order_items VALUES (4, 5, 1);


--
-- TOC entry 4953 (class 0 OID 0)
-- Dependencies: 221
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 5, true);


--
-- TOC entry 4954 (class 0 OID 0)
-- Dependencies: 225
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 4, true);


--
-- TOC entry 4955 (class 0 OID 0)
-- Dependencies: 223
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 6, true);


--
-- TOC entry 4956 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


-- Completed on 2026-08-01 09:41:33

--
-- PostgreSQL database dump complete
--

\unrestrict Do2jPGxGe31kwY1AqZqkaE6xf5MnV76MBjlyhQym5URRcFQly3xjhZ0tgekvq49

