# Day 20: Networking under time pressure

- Course: Course 2, the depth month
- Why: Timed practice on real network breakages, plus how kube-proxy turns a Service IP into a pod.
- Minimum version (low-energy day): Do only 'Jakarta'.

## Block 1. jq on kubectl (Warm-up, 15 min, where: kind cluster)

- Services and their endpoints:

  ```bash
  k get svc -A -o json | jq -r '.items[] | .metadata.namespace + "/" + .metadata.name + " " + .spec.type + " " + (.spec.clusterIP // "none")'
  k get endpointslices -A -o json | jq -r '.items[] | .metadata.name + " " + ([.endpoints[]?.addresses[]] | join(","))'
  ```

Done when: Both queries ran.

## Block 2. Read: the life of a packet in Kubernetes (Learn, 30 min, where: Browser)

- [Life of a Packet in Kubernetes, Part 3](https://dramasamy.medium.com/life-of-a-packet-in-kubernetes-part-3-dd881476da0f) by Dinesh Kumar Ramasamy: kube-proxy and iptables.

Done when: You can say what KUBE-SERVICES and KUBE-SEP chains do.

## Block 3. Lab: three network scenarios against the clock (Lab, 90 min, where: Browser)

- Start each one the same way: what's listening (`ss -tulpn`), what resolves (`getent hosts`), and what the logs say (`journalctl -xe`).
- SadServers 'Jakarta' (30 min).
- SadServers 'Bern' (30 min).
- SadServers 'Melbourne' (30 min).

Done when: Three scenarios attempted, each within 30 minutes.

## Block 4. Prove it (Prove it, 15 min, where: Repo)

- Add a 3-line postmortem for each scenario to `cards/13-postmortems.md` and push it.

Done when: Three postmortems added.

## Block 5. CKA: series Days 32–33 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 32–33: Kubernetes networking and Ingress. Do the tasks for [Day 32](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day32) and [Day 33](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day33).
- Extra: see the rules kube-proxy wrote. Run `docker exec kind-control-plane iptables -t nat -L KUBE-SERVICES -n | head` (use your control-plane container's name).

Done when: Both tasks done and you found your Service in KUBE-SERVICES.

## Block 6. Post and apply (Job hunt, 30 min, where: Laptop)

- Publish LinkedIn post #2: 'I built container networking by hand with namespaces, veth pairs and a bridge'. Add the photo of your packet-path drawing.
- Apply to 2 roles and log them.

Done when: Post published and 2 applications logged.
