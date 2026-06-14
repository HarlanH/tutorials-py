def binary_search(arr, target, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    if low > high:
        return -1
    mid = (low + high) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, high)
    else:
        return binary_search(arr, target, low, mid - 1)


if __name__ == "__main__":
    arr = list(range(0, 20, 2))
    print(f"Array: {arr}")
    for target in [6, 7, 14]:
        idx = binary_search(arr, target)
        print(f"Search {target}: index {idx}")
