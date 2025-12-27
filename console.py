def twoSum(nums, target):
    # nums = [11, 2, 7, 15]
    # target = 9
    a = 0
    b = 0
    while True:
        if nums[a] + nums[b] == target:
            b+=b
            print(nums[a], nums[b])
        else:
            a += a
        print(a)



twoSum(nums=[11, 2, 7, 15], target=9)
